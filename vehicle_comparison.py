#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FormatStrFormatter
import os
import pandas.testing as tm
from scipy.stats import gamma
plt.rcParams.update({'figure.autolayout': True, 'font.size': 14, })
plt.rcParams["font.family"] = "Helvetica"
plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

vclass = ["Medium duty truck", 'Small diesel van', 'Medium duty electric truck',
          'Small electric van', 'Electric cargo bicycle', 
          'Quad-copter drone']
n = (0.95*0.88) # 88% charging efficiency and 5% transmission losses 
eff = np.array([1, 1, n, n, n, n])
e = np.array([11, 4.9, 3.13, 1.36, 0.083, 0.039])/eff
ghg_fuel = np.array([69.5, 69.5, 182, 182, 182, 182])*e
ghg_upstream = np.array([15.34, 15.34, 22, 22, 22, 22])*e
#ghg_battery = np.array([0, 0, 16.6, 16.6, 16.6, 5.9])*e
GHG_energy = np.array([107, 182, 249])
GHG_battery = np.array([10.1, 33.7, 67.3])

df = pd.DataFrame({"vclass":vclass, "energy": e, "ghg_fuel": ghg_fuel, "ghg_upstream": ghg_upstream})
df['e_high'] = df.energy*0.2
df['e_low'] = df.energy*0.2
df.loc[5,["e_high","e_low"]] = 0



df1 = df.sort_values(by = ['energy'], ascending=True).copy()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24,6))

color_others = "#9F9F9F"
ax1.barh(df1.vclass, df1.energy , color = ["blue", color_others, color_others, color_others, color_others, color_others ],
         xerr= np.array([df1.e_low,df1.e_high]), capsize =5)
ax1.set_xticklabels(ax1.get_xticks(), Fontsize=26)
ax1.set_yticklabels(df1.vclass,Fontsize=28)
sns.despine(top=True, right=True)
ax1.set_xlabel('Energy Consumption [MJ/km]\n(a)', fontsize=28)

stop_km = np.array([0.7, 1.74, 0.7, 1.74, 1, 0.25])
pack_stop = np.array([3, 2, 3, 2, 1, 1])
pack_km = pack_stop*stop_km
e_pack = df.energy/pack_km

pack_km_high = np.array([1.5, 1.5, 1.5, 1.5, 0.25, 0.125])
pack_km_low = np.array([5, 5, 5, 5, 3, 0.5])

df['e_pack'] = df.energy/pack_km
df['e_pack_low'] = np.fabs(df.energy/pack_km_low - df.e_pack)
df['e_pack_high'] = np.fabs(df.energy/pack_km_high - df.e_pack)

df1 = df.sort_values(by = ['e_pack'], ascending=True).copy()

color_others = "#9F9F9F"

ax2.barh(df1.vclass, df1.e_pack , color = [color_others, "blue", color_others, color_others, color_others, color_others],
         xerr= np.array([df1.e_pack_low,df1.e_pack_high]), capsize =5)

ax2.set_xticklabels(ax2.get_xticks(), fontsize=26)
ax2.set_yticklabels(df1.vclass, fontsize=28)
sns.despine(top=True, right=True)
ax2.set_xlabel('Energy consumption [MJ/Package]\n(b)', fontsize=28)
plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
ax1.xaxis.set_major_formatter(FormatStrFormatter('%d'))
ax2.xaxis.set_major_formatter(FormatStrFormatter('%d'))
plt.savefig("figure2.pdf")
plt.show()



ghg_fuel = np.array([69.5, 69.5, 182, 182, 182, 182])
ghg_upstream = np.array([15.34, 15.34, 22, 22, 22, 22])
#ghg_battery = np.array([0, 0, 16.6, 16.6, 16.6, 5.9])

ghg_fuel_low = np.array([69.5, 69.5, 107, 107, 107, 107])

ghg_fuel_high = np.array([69.5, 69.5, 249, 249, 249, 249])

df["ghg_km_fuel"] = df.energy*ghg_fuel
df['ghg_km_upstream'] = df.energy*ghg_upstream
df['ghg_km_battery'] = np.array([0, 0, 24.5, 14.1, 1.3, 0.76])
df['ghg_km_battery_high'] = np.array([0, 0, 24.5, 14.1, 1.3, 1.52])
df['ghg_km_battery_low'] = np.array([0, 0, 24.5, 14.1, 1.3, 0.23])

df["ghg_km_fuel_low"] = df.energy*ghg_fuel_low*(0.8)
df["ghg_km_fuel_high"] = df.energy*ghg_fuel_high*(1.2)

df['ghg_base'] = df.ghg_km_fuel + df.ghg_km_upstream + df.ghg_km_battery
df['ghg_high'] = df.ghg_km_fuel_high + df.ghg_km_upstream + df.ghg_km_battery_high
df['ghg_low'] = df.ghg_km_fuel_low + df.ghg_km_upstream + df.ghg_km_battery_low

df['ghg_error_high'] = df.ghg_high - df.ghg_base 
df['ghg_error_low'] = df.ghg_base - df.ghg_low


df1 = df.sort_values(by = ['ghg_fuel'], ascending=True).copy()


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24,6))



ax1.barh(df1.vclass, df1.ghg_km_upstream, color='gray', label = 'Upstream fuel')
ax1.barh(df1.vclass, df1.ghg_km_battery, color='orange', left= df1.ghg_km_upstream, label = 'Battery lifecycle')
ax1.barh(df1.vclass, df1.ghg_km_fuel, color = 'lightblue', left=df1.ghg_km_battery + df1.ghg_km_upstream,
         label = 'Fuel consumption', xerr= np.array([df1.ghg_error_low,df1.ghg_error_low]), capsize =5)
ax1.legend(title = 'Emission source', frameon=False)

ax1.set_xticklabels(ax1.get_xticks(), Fontsize=26)
ax1.set_yticklabels(df1.vclass, Fontsize=28)
sns.despine(top=True, right=True)
ax1.set_xlabel('CO₂e emissions [g/km]\n(a)', fontsize=28)
plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)


# In[8]:


stop_km = np.array([0.7, 1.74, 0.7, 1.74, 1, 0.25])
pack_stop = np.array([3, 2, 3, 2, 1, 1])
pack_km = pack_stop*stop_km

pack_km_high = np.array([1.5, 1.5, 1.5, 1.5, 0.25, 0.125])
pack_km_low = np.array([5, 5, 5, 5, 3, 0.5])

df['ghg_fuel_pack'] = df.ghg_km_fuel/pack_km
df['ghg_upstream_pack'] = df.ghg_km_upstream/pack_km
df['ghg_battery_pack'] = df.ghg_km_battery/pack_km

df['ghg_fuel_pack_low'] = df.ghg_km_fuel/pack_km_low
df['ghg_upstream_pack_low'] = df.ghg_km_upstream/pack_km_low
df['ghg_battery_pack_low'] = df.ghg_km_battery/pack_km_low

df['ghg_fuel_pack_high'] = df.ghg_km_fuel/pack_km_high
df['ghg_upstream_pack_high'] = df.ghg_km_upstream/pack_km_high
df['ghg_battery_pack_high'] = df.ghg_km_battery/pack_km_high

df['ghg_base_pack'] = df.ghg_fuel_pack + df.ghg_upstream_pack + df.ghg_battery_pack
df['ghg_high_pack'] = df.ghg_fuel_pack_high + df.ghg_upstream_pack_high + df.ghg_battery_pack_high
df['ghg_low_pack'] = df.ghg_fuel_pack_low + df.ghg_upstream_pack_low + df.ghg_battery_pack_low

df['ghg_error_high_pack'] = df.ghg_high_pack - df.ghg_base_pack
df['ghg_error_low_pack'] = df.ghg_base_pack - df.ghg_low_pack


df1 = df.sort_values(by = ['ghg_base_pack'], ascending=True).copy()

ax2.barh(df1.vclass, df1.ghg_upstream_pack, color='gray', label = 'Upstream fuel')
ax2.barh(df1.vclass, df1.ghg_battery_pack, color='orange', left= df1.ghg_upstream_pack, label = 'Battery lifecycle')
ax2.barh(df1.vclass, df1.ghg_fuel_pack, color = 'lightblue', left=df1.ghg_battery_pack + df1.ghg_upstream_pack,
         label = 'Fuel consumption', xerr= np.array([df1.ghg_error_low_pack,df1.ghg_error_high_pack]), capsize =5)
ax2.legend(title = 'Emission source', frameon=False)

ax2.set_xticklabels(ax1.get_xticks(), Fontsize=26)
ax2.set_yticklabels(df1.vclass,Fontsize=28)
sns.despine(top=True, right=True)
ax2.set_xlabel('CO₂e emissions [g/package]\n(b)', fontsize=28)

ax2.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
ax1.xaxis.set_major_formatter(FormatStrFormatter('%d'))
ax2.xaxis.set_major_formatter(FormatStrFormatter('%d'))
plt.savefig("figure3.pdf")
plt.show()


# In[9]:


df.columns


# In[10]:


df.ghg_base_pack


# In[11]:


data = df.loc[:,['vclass','energy', 'ghg_fuel','ghg_upstream', 'ghg_km_battery', 'e_pack', 'ghg_base_pack']].copy()
data.rename(columns = {'vclass':'Vehicle Class', 'energy': 'Energy Consumption [MJ/km]',
                      'ghg_fuel': 'Fuel GHG emissions [g/km]', 'ghg_upstream':'Upstream GHG emissions [g/km]',
                       'ghg_km_battery': 'Battery GHG emissions [g/km]',
                       'e_pack':'Energy consumption [MJ/package]', 'ghg_base_pack': 'GHG emission [g/package]'}, inplace=True)
data.to_csv('summary_energy_emissions.csv', index=False)


# In[12]:


a = 1


# In[13]:


df.ghg_km_battery


# In[14]:


df = pd.read_csv('summary_energy_emissions.csv')
df['max_payload'] = [4400,4400,2500,2500,95,1]


# In[15]:


df['tonkm'] = (df['Energy Consumption [MJ/km]']/df.max_payload)*1000


# In[16]:


df


# In[17]:


df1 = df.sort_values(by = ['tonkm'], ascending=True).copy()

plt.figure(figsize=(14,8))
color_others = "#9F9F9F"

plt.figure(figsize=(14,6))

plt.barh(df1['Vehicle Class'], df1.tonkm , color = [color_others, color_others, color_others, color_others, color_others, "blue"], 
         xerr= np.array([0.2*df1.tonkm,0.2*df1.tonkm]), capsize =5)

plt.xticks(fontsize=26)
plt.yticks(fontsize=28)
sns.despine(top=True, right=True)
plt.xlabel('Energy consumption [MJ/ton-km]', fontsize=28)
plt.savefig("energy_tonkm.png")
plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
plt.show()


# In[ ]:





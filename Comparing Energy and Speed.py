import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams.update({'figure.autolayout': True, 'font.size': 14, })
plt.rcParams["font.family"] = "Helvetica"
plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

df = pd.read_csv("energy_summary_model1.csv")
sns.boxplot(df.speed, df.Power_cruise, color="magenta")
#sns.scatterplot(df.speed, df.Power_cruise, hue=df.payload, x_jitter=True)
#sns.boxplot(df.speed, df.Power_cruise, hue=df.payload)
#sns.scatterplot(df.speed, df.Power_takeoff)
#sns.scatterplot(df.speed, df.Power_landing)
plt.ylabel("Average power \nduring cruise [Wh]", fontsize=14)
plt.xlabel("Speed [m/s]", fontsize=14)
plt.ylim(0,650)
sns.despine(top=True, right=True)
plt.savefig('power_speed.png', dpi=500)
#plt.show()

test = df[['speed', 'Power_cruise', 'payload']].copy()
test.to_csv('speed_test.csv', index=False)

power=[]
for speed in set(df.speed):
    power.append(df.loc[df.speed==speed,'Power_cruise'].mean())

print(power)
print(np.array(power)/power[0])
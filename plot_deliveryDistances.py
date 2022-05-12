import pandas as pd
import matplotlib.pyplot as plt
from calculate_energy import energy_two_way
import numpy as np
import seaborn as sns
import os


def two_way_energy():
    '''
    This function plots Figure 1a
    :return:
    '''
    mainpath= os.getcwd()
    plt.rcParams.update({'figure.autolayout': True})
    plt.rcParams["font.family"] = "Helvetica"
    plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})

    coeff = pd.read_csv('coefficients_model1.csv', index_col=0)

    distance = np.arange(0,8.5,0.01)
    e_1000 = [energy_two_way(d, coeff, payload=1000, speed=12) for d in distance]
    e_500 = [energy_two_way(d, coeff, payload=500, speed=12) for d in distance]
    e_0 = [energy_two_way(d, coeff, payload=0, speed=12) for d in distance]
    e_1000_4 = [energy_two_way(d, coeff, payload=1000, speed=4) for d in distance]
    e_500_4 = [energy_two_way(d, coeff, payload=500, speed=4) for d in distance]
    e_0_4 = [energy_two_way(d, coeff, payload=0, speed=4) for d in distance]

    df_dist = pd.DataFrame({"d" : distance, "e_1000" : e_1000, "e_500" : e_500, "e_0" : e_0, "e_1000_4": e_1000_4, "e_500_4": e_500_4, "e_0_4": e_0_4})
    df_dist[df_dist > 129.96] = None
    print(df_dist[(df_dist.d > 3.9)&(df_dist.d < 4.1)])
    plt.figure(figsize=(10,6))
    plt.plot(df_dist.d, df_dist.e_1000_4, color='red')
    plt.plot(df_dist.d, df_dist.e_1000, color='blue')
    plt.plot(df_dist.d, df_dist.e_500, color='blue')
    plt.plot(df_dist.d, df_dist.e_0, color='blue')
    plt.plot(df_dist.d, df_dist.e_500_4, color='red')
    plt.plot(df_dist.d, df_dist.e_0_4, color='red')
    plt.ylim(0, 145)
    xlim_max = 8.5
    plt.xlim(0, xlim_max)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.axhline(129.96, xmin=0, xmax=xlim_max, color='gray', linestyle=(0, (3, 5, 1, 5)), alpha=0.5)

    sns.despine(top=True, right=True)
    plt.xlabel('Delivery Distance [km]', fontsize=18)
    plt.ylabel('Total Energy Consumption \ntwo-way delivery [Wh/package]', fontsize=18)
    plt.text(2.6, 131, 'LiPo Battery Capacity', color="gray", fontsize=14)
    plt.text(4.0, 95, '1 kg', rotation=38, fontsize=12, color="gray")
    plt.text(4.7, 95, '500 g', rotation=33, fontsize=12, color="gray")
    plt.text(5.6, 95, 'No payload', rotation=28, fontsize=12, color="gray")
    plt.text(1.2, 95, '1 kg', rotation=62, fontsize=12, color="gray")
    plt.text(1.5, 95, '500 g', rotation=60, fontsize=12, color="gray")
    plt.text(1.8, 95, 'No payload', rotation=57, fontsize=12, color="gray")
    plt.legend(['4 m/s', "12 m/s"], title='Cruise speed', fontsize=14, frameon=False).get_title().set_fontsize(14)
    os.chdir(r"C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Paper")
    plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
    plt.savefig('two_way_distance.pdf')
    os.chdir(mainpath)
    plt.show()

def two_way_ghg():
    '''
    This function plots Figure 1b
    :return:
    '''
    plt.rcParams.update({'figure.autolayout': True})
    plt.rcParams["font.family"] = "Helvetica"
    plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})

    coeff = pd.read_csv('coefficients_model1.csv', index_col=0)

    distance = np.arange(0,6.5,0.01)
    e_1000 = [energy_two_way(d, coeff, payload=1000, speed=12) for d in distance]

    df_dist = pd.DataFrame({"d" : distance, "e_1000" : e_1000})
    ghg_electricity = [107, 182, 249]
    ghg_upstream = 22
    ghg_battery = [1.3, 4.2, 8.5]
    df_dist = df_dist[df_dist <= 129.96].copy()
    df_dist['e'] = df_dist.e_1000*0.0036
    df_dist['ghg'] = df_dist.e*(ghg_electricity[1] + ghg_upstream + ghg_battery[1])
    df_dist['ghg_low'] = df_dist.e*(ghg_electricity[0] + ghg_upstream + ghg_battery[0])
    df_dist['ghg_high'] = df_dist.e*(ghg_electricity[2] + ghg_upstream + ghg_battery[2])

    plt.figure(figsize=(10,6))
    plt.plot(df_dist.d, df_dist.ghg, color='blue')
    plt.fill_between(df_dist.d,df_dist.ghg_low, df_dist.ghg_high, color ='gray', alpha=0.5)
    #plt.ylim(0, 145)
    xlim_max = 6.5
    plt.xlim(0, xlim_max)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    sns.despine(top=True, right=True)
    plt.xlabel('Delivery Distance [km]', fontsize=18)
    plt.ylabel('CO₂e emissions \ntwo-way delivery [g/package]', fontsize=18)
    os.chdir(r"C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Paper")
    plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
    plt.savefig('two_way_ghg.pdf')
    plt.show()

def figure1():
    mainpath = os.getcwd()
    plt.rcParams.update({'figure.autolayout': True})
    plt.rcParams["font.family"] = "Helvetica"
    plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})

    coeff = pd.read_csv('coefficients_model1.csv', index_col=0)
    print(coeff)

    distance = np.arange(0, 8.5, 0.01)
    e_1000 = [energy_two_way(d, coeff, payload=1000, speed=12) for d in distance]
    e_500 = [energy_two_way(d, coeff, payload=500, speed=12) for d in distance]
    e_0 = [energy_two_way(d, coeff, payload=0, speed=12) for d in distance]
    e_1000_4 = [energy_two_way(d, coeff, payload=1000, speed=4) for d in distance]
    e_500_4 = [energy_two_way(d, coeff, payload=500, speed=4) for d in distance]
    e_0_4 = [energy_two_way(d, coeff, payload=0, speed=4) for d in distance]

    df_dist = pd.DataFrame(
        {"d": distance, "e_1000": e_1000, "e_500": e_500, "e_0": e_0, "e_1000_4": e_1000_4, "e_500_4": e_500_4,
         "e_0_4": e_0_4})
    df_dist[df_dist > 129.96] = None
    print(df_dist[(df_dist.d > 3.9) & (df_dist.d < 4.1)])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,6))

    #ax1.plot(df_dist.d, df_dist.e_1000_4, color='red')
    #ax1.plot(df_dist.d, df_dist.e_1000, color='blue')
    ax1.plot(df_dist.d, df_dist.e_500_4, color='red')
    ax1.plot(df_dist.d, df_dist.e_500, color='blue')

    ax1.plot(df_dist.d, df_dist.e_0, color='blue')
    ax1.plot(df_dist.d, df_dist.e_0_4, color='red')
    ax1.set_ylim(0, 145)
    xlim_max = 5
    ax1.set_xlim(0, xlim_max)
    ax1.set_xticklabels(ax1.get_xticks(), fontsize=16)
    ax1.set_yticklabels(ax1.get_yticks(), fontsize=16)
    ax1.axhline(129.96, xmin=0, xmax=xlim_max, color='gray', linestyle=(0, (3, 5, 1, 5)), alpha=0.5)

    sns.despine(top=True, right=True)
    ax1.set_xlabel('Delivery Distance [km]\n(a)', fontsize=18)
    ax1.set_ylabel('Total Energy Consumption \ntwo-way delivery [Wh/package]', fontsize=18)
    ax1.text(2.0, 131, 'LiPo Battery Capacity', color="black", fontsize=14)
    #ax1.text(4.0, 95, '1 kg', rotation=38, fontsize=12, color="gray")
    ax1.text(2.7, 95, '500 g', rotation=30, fontsize=12, color="gray")
    ax1.text(3.5, 95, 'No payload', rotation=18.2, fontsize=12, color="gray")
    #ax1.text(1.2, 95, '1 kg', rotation=62, fontsize=12, color="gray")
    ax1.text(0.8, 95, '500 g', rotation=60, fontsize=12, color="gray")
    ax1.text(1.2, 95, 'No payload', rotation=54., fontsize=12, color="gray")
    ax1.legend(['4 m/s', "12 m/s"], title='Cruise speed', fontsize=14, frameon=False).get_title().set_fontsize(14)
    ax1.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
    coeff = pd.read_csv('coefficients_model1.csv', index_col=0)

    distance = np.arange(0, 6.5, 0.01)
    e_1000 = [energy_two_way(d, coeff, payload=500, speed=12) for d in distance]

    df_dist = pd.DataFrame({"d": distance, "e_1000": e_1000})
    ghg_electricity = [111, 177, 250]
    ghg_upstream = 22
    ghg_battery = [1.3, 4.2, 8.5]
    df_dist = df_dist[df_dist <= 129.96].copy()
    df_dist['e'] = df_dist.e_1000 * 0.0036
    df_dist['ghg'] = df_dist.e * (ghg_electricity[1] + ghg_upstream + ghg_battery[1])
    df_dist['ghg_low'] = df_dist.e * (ghg_electricity[0] + ghg_upstream + ghg_battery[0])
    df_dist['ghg_high'] = df_dist.e * (ghg_electricity[2] + ghg_upstream + ghg_battery[2])

    ax2.plot(df_dist.d, df_dist.ghg, color='blue')
    ax2.fill_between(df_dist.d, df_dist.ghg_low, df_dist.ghg_high, color='gray', alpha=0.5)
    #plt.ylim(0, 145)
    xlim_max = 4.1
    ax2.set_xlim(0, xlim_max)
    ax2.set_xticklabels(ax2.get_xticks(), fontsize=16)
    ax2.set_yticklabels(ax2.get_xticks(), fontsize=16)

    sns.despine(top=True, right=True)
    ax2.set_xlabel('Delivery Distance [km]\n(b)', fontsize=18)
    ax2.set_ylabel('CO₂e emissions \ntwo-way delivery [g/package]', fontsize=18)
    os.chdir(r"C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Paper")
    plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
    os.chdir(r"C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Paper\energy_model")

    plt.savefig("figure1.pdf")
    plt.show()


def main():
    figure1()


if __name__ == "__main__":
    main()
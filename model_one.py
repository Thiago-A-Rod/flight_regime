import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import FindingRegimeFilter
import scipy.integrate
import inflightcomponents as inflight
import matplotlib.ticker as mtick
import LinearRegression as lr
import FindingRegime2
import airdensity

plt.rcParams["font.family"] = "Helvetica"
plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

def avg_power_summary(df):
    #takeOff, landing, cruise, wholeflight = FindingRegimeFilter.FindRegime(df)
    takeOff, landing, cruise, wholeflight = FindingRegime2.find_regime(df)
    time_cruise = cruise['time'].max() - cruise['time'].min()
    time_takeoff = takeOff['time'].max() - takeOff['time'].min()
    time_landing = landing['time'].max() - landing['time'].min()
    time_whole = wholeflight['time'].max() - wholeflight['time'].min()

    e_measured_cruise = scipy.integrate.simps(cruise['Power'], x=cruise["time"], even="avg") / 3600
    e_measured_takeoff = scipy.integrate.simps(takeOff['Power'], x=takeOff["time"], even="avg") / 3600
    e_measured_landing = scipy.integrate.simps(landing['Power'], x=landing["time"], even="avg") / 3600
    e_measured_whole = scipy.integrate.simps(wholeflight['Power'], x=wholeflight["time"], even="avg") / 3600
    return e_measured_takeoff, e_measured_cruise, e_measured_landing, e_measured_whole,\
           time_takeoff, time_cruise, time_landing, time_whole


def create_energy_summary(data):
    '''
    :param data: data frame with all flights
    :return: creates a csv with an energy summary
    '''

    energy_summary = pd.DataFrame()
    index = list(set(data['flight']))
    i = 1
    for flight in index:
        print('flight: %d progress = %d%%'%(flight, i*100/len(index)) , end='\r')
        df = data[data['flight'] == flight].copy()
        payload = df.payload.min()
        speed = df.speed.min()
        altitude = df.altitude.min()
        Pi_hover = inflight.hoverInducedPower(df)
        e_tk, e_cr, e_ld, e_wl, t_tk, t_cr, t_ld, t_wl = avg_power_summary(df)
        energy_flight = pd.DataFrame({'flight': [flight], 'payload': [payload], "altitude": [altitude],
                                      'speed': [speed], 'Energy_takeoff': e_tk, 'Energy_cruise': e_cr,
                                      'Energy_landing': e_ld, 'Energy_total': e_wl, 'time_takeoff': t_tk,
                                      'time_cruise':  t_cr, 'time_landing': t_ld, 'time_total': t_wl,
                                      'Power_takeoff': e_tk * 3600 / t_tk, 'Power_cruise': e_cr * 3600 / t_cr,
                                      'Power_landing': e_ld * 3600 / t_ld, "avg_power": e_wl*3600/t_wl,
                                      "Pi_hover": Pi_hover})
        energy_summary = energy_summary.append(energy_flight, ignore_index=True)
        i += 1
    energy_summary.to_csv('energy_summary_model1.csv', index=False)

    print("Energy Summary Created as energy_summary_model1.csv")

def energy(distance, coeff, payload=500, speed=12, altitude=100):
    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    m = 3.08 + 0.635
    rho = 1.20
    Pi_unload = ((m * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)
    Pi_load = (((m + payload / 1000) * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)

    b1_tk = coeff.loc['takeoff', 'b1']
    b0_tk = coeff.loc['takeoff', 'b0']
    b1_cr = coeff.loc['cruise', 'b1']
    b0_cr = coeff.loc['cruise', 'b0']
    b1_ld = coeff.loc['landing', 'b1']
    b0_ld = coeff.loc['landing', 'b0']

    d = distance * 1000
    V = speed
    t = d/V
    Energy_tk1 = (Pi_load * b1_tk + b0_tk) * (altitude/2.5) / 3600 # assumes a 40 second takeoff
    Energy_cr1 = (Pi_load * b1_cr + b0_cr) * t / 3600
    Energy_ld1 = (Pi_load * b1_ld + b0_ld) * (altitude/2.0) / 3600 # assumes a 50 second landing
    Energy_tk2 = (Pi_unload * b1_tk + b0_tk) * (altitude/2.5) / 3600
    Energy_cr2 = (Pi_unload * b1_cr + b0_cr) * t / 3600
    Energy_ld2 = (Pi_unload * b1_ld + b0_ld) * (altitude/2.0) / 3600

    Total_Energy = Energy_tk1 + Energy_cr1 + Energy_ld1 + Energy_tk2 + Energy_cr2 + Energy_ld2
    return Total_Energy


def energy_one_way(distance, coeff, payload=500, speed=12, altitude = 100):
    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    m = 3.08 + 0.635
    rho = 1.20
    Pi_load = (((m + payload / 1000) * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)

    b1_tk = coeff.loc['takeoff', 'b1']
    b0_tk = coeff.loc['takeoff', 'b0']
    b1_cr = coeff.loc['cruise', 'b1']
    b0_cr = coeff.loc['cruise', 'b0']
    b1_ld = coeff.loc['landing', 'b1']
    b0_ld = coeff.loc['landing', 'b0']

    d = distance * 1000
    V = speed
    t = d / V

    Energy_tk1 = (Pi_load * b1_tk + b0_tk) * (altitude/2.5) / 3600  # assumes a 40 second takeoff
    Energy_cr1 = (Pi_load * b1_cr + b0_cr) * t / 3600
    Energy_ld1 = (Pi_load * b1_ld + b0_ld) * (altitude/2.0) / 3600  # assumes a 50 second landing

    Total_Energy = Energy_tk1 + Energy_cr1 + Energy_ld1
    return Total_Energy

def main():
    mainpath = os.getcwd()
    os.chdir(r'C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Data\Review\data\Kilthub')
    data = pd.read_csv('flights.csv', low_memory=False)
    data = data[((data.route == 'R1')|(data.route == 'R2')|(data.route == 'R3')|(data.route == 'R4')|(data.route == 'R5'))&(
        data.payload < 750)]
    index = list(set(data['flight']))
    data['Power'] = data['battery_current']*data['battery_voltage']
    print(data.columns)
    #airdensity.CreateCsv(data, mainpath)
    create_summary = input('Enter "y" to create the energy summary: ')
    #create_summary = 'no'
    os.chdir(mainpath)
    if create_summary == 'y':
        create_energy_summary(data)


    summary = pd.read_csv('energy_summary_model1.csv')
    pool = pd.read_csv('pool.csv')
    summary.payload = summary.payload.astype(int)
    summary_pool = summary[summary.flight.isin(pool.flight)].copy()
    #print(summary_pool)



    palette = sns.color_palette(None, 3)
    fig, ax = plt.subplots()
    ax.set_ylim(0, 650)
    ax.set_xlim(255, 335)
    g = sns.scatterplot(x='Pi_hover', y='avg_power', data=summary, hue='payload', palette=palette)
    # g = sns.regplot(x='Pi_hover', y='avg_power', data=summary)
    plt.xlabel('Induced Power [W]', fontsize=24)
    plt.ylabel('Average Power [W]', fontsize=24)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[1:], labels=labels[1:], title='Payload [g]', frameon=False, loc='lower center', ncol=4)
    sns.despine(top=True, right=True)


    g.set_yticklabels(g.get_yticks(), size=14)
    g.set_xticklabels(g.get_xticks(), size=14)

    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
    ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
    ax.grid(b=True, which='major', color='gray', linewidth=1.0, alpha=0.1)
    #print(summary.columns)
    coeff = lr.linear_regression(summary)
    print(coeff)
    x = np.linspace(260, 330)
    y = x*coeff.loc['total','b1'] + coeff.loc['total','b0']
    plt.plot(x, y, color='black', linestyle='-.', alpha=0.5)
    coeff = lr.linear_regression(summary_pool)
    print(coeff)


    print(summary)
    summary['e_tk'] = (summary.Pi_hover * coeff.loc['takeoff','b1'] + coeff.loc['takeoff','b0'])*summary.time_takeoff/3600
    summary['e_cr'] = (summary.Pi_hover * coeff.loc['cruise', 'b1'] + coeff.loc['cruise', 'b0'])*summary.time_cruise/3600
    summary['e_ld'] = (summary.Pi_hover * coeff.loc['landing', 'b1'] + coeff.loc['landing', 'b0'])*summary.time_landing/3600
    summary['e_total'] = (summary.Pi_hover * coeff.loc['total', 'b1'] + coeff.loc['total', 'b0'])*summary.time_total/3600
    summary['error_tk'] = (summary.Energy_takeoff - summary.e_tk) / summary.Energy_takeoff
    summary['error_cr'] = (summary.Energy_cruise - summary.e_cr) / summary.Energy_cruise
    summary['error_ld'] = (summary.Energy_landing - summary.e_ld) / summary.Energy_landing
    summary['error_total'] = (summary.Energy_total - summary.e_total) / summary.Energy_total

    summary.to_csv('energy_projection.csv',index=False)


if __name__ == "__main__":
    main()
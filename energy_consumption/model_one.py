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

plt.rcParams["font.family"] = "Helvetica"
plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

def avg_power_summary(df):
    takeOff, landing, cruise, wholeflight = FindingRegimeFilter.FindRegime(df)
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

def test(df, coeff):
    b1_tk = coeff.loc['takeoff', 'b1']
    b0_tk = coeff.loc['takeoff', 'b0']
    b1_cr = coeff.loc['cruise', 'b1']
    b0_cr = coeff.loc['cruise', 'b0']
    b1_ld = coeff.loc['landing', 'b1']
    b0_ld = coeff.loc['landing', 'b0']
    Pi = df.Pi_hover
    t_tk = df.time_takeoff
    t_cr = df.time_cruise
    t_ld = df.time_landing

    return (t_tk*(b1_tk*Pi+b0_tk) + t_cr*(b1_cr*Pi+b0_cr) + t_ld*(b1_ld*Pi+b0_ld))/3600

def ARE(df):
    return np.fabs(df.Energy_total - df.energy_model)/df.Energy_total

def main():
    data = pd.read_csv('flights.csv', low_memory=False)
    data = data[((data.route == 'R1')|(data.route == 'R2')|(data.route == 'R3')|(data.route == 'R4')|(data.route == 'R5'))&(
        data.payload < 750)]
    index = list(set(data['flight']))
    data['Power'] = data['battery_current']*data['battery_voltage']
    try:
        summary = pd.read_csv('Energy_summary_model1.csv')
    except:
        create_energy_summary(data)
        summary = pd.read_csv('Energy_summary_model1.csv')
    poll = pd.DataFrame({"flight":np.random.choice(index, size=120, replace=False)})
    poll = pd.read_csv('poll.csv')  # <-- poll of flights used
    summary.payload = summary.payload.astype(int)
    summary_poll = summary[summary.flight.isin(poll.flight)].copy()

    coeff = lr.linear_regression(summary_poll)
    test_sample = summary[~summary.flight.isin(poll.flight)].copy()
    test_sample['energy_model'] = test(test_sample, coeff)
    test_sample["ARE"] = ARE(test_sample)
    test_sample.to_csv('Test_model_1.csv', index=False)
    print("ARE: Average = %.4f; Median = %.4f"%(test_sample.ARE.mean(), test_sample.ARE.median()))

if __name__ == "__main__":
    main()
# This module creates an energy summary of the files

import pandas as pd
import numpy as np
import os
import FindingRegimeFilter
import scipy.integrate
import inflightcomponents as inflight
import matplotlib.ticker as mtick
import LinearRegression as lr



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
    return e_measured_takeoff, e_measured_cruise, e_measured_landing, e_measured_whole, time_takeoff, time_cruise, time_landing, time_whole


def create_energy_summary(data):
    '''
    :param data: data frame with all flights
    :return: creates a csv with an energy summary
    '''
    print('Creating energy summary')
    energy_summary = pd.DataFrame()
    index = list(set(data['flight']))
    i = 1
    for flight in index:
        print('flight: %d; Overall progress = %d%%'%(flight, i*100/len(index)) , end='\r')
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

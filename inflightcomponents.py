import pandas as pd
import numpy as np
import power_functions as pwf
import os
import matplotlib.pyplot as plt
#import fixColumn as fix
import airdensity
import FindingRegimeFilter
import inducedVelocity
import scipy.integrate
import time
from geopy.distance import geodesic

def hoverInducedPower(df):
    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    payload = df.payload.min()
    m = payload / 1000 + 3.08 + 0.635
    rho = airdensity.AirDensity(df)
    #return ((m*gravity)**(3/2))/np.sqrt(2*rho*A) # commented to exclude A and g
    return ((m) ** (3 / 2)) / np.sqrt(rho)

def energyMeasured(df):
    df['Power']= df['battery_current']*df['battery_voltage']
    takeOff, landing, cruise, wholeflight = FindingRegimeFilter.FindRegime(df)
    df_cruise = cruise
    df_takeOff = takeOff
    df_landing = landing
    time_cruise = df_cruise['time'].max() - df_cruise['time'].min()
    time_takeoff = df_takeOff['time'].max() - df_takeOff['time'].min()
    time_landing = df_landing['time'].max() - df_landing['time'].min()

    energy_measured_cruise = scipy.integrate.simps(df_cruise['Power'], x=df_cruise["time"], even="avg") / 3600
    energy_measured_takeoff = scipy.integrate.simps(df_takeOff['Power'], x=df_takeOff["time"], even="avg") / 3600
    energy_measured_landing = scipy.integrate.simps(df_landing['Power'], x=df_landing["time"], even="avg") / 3600

    energy_measured_total = energy_measured_takeoff + energy_measured_cruise + energy_measured_landing

    return time_takeoff, time_cruise, time_landing, energy_measured_total


def total_distance(df):
    distance = 0
    lat_N = df['x'][df.index.values[0]]
    lon_W = df['y'][df.index.values[0]]
    coord1 = (lat_N, lon_W)
    for record in df.index.values:
        coord2 = (df['x'][record], df['y'][record])
        distance += geodesic(coord1,coord2).km
        coord1 = coord2
    return distance

def energy_measured_regime(df):
    df['Power'] = df['battery_current'] * df['battery_voltage']
    takeOff, landing, cruise, wholeflight = FindingRegimeFilter.FindRegime(df)
    df_cruise = cruise
    df_takeOff = takeOff
    df_landing = landing
    t_cruise = df_cruise['time'].max() - df_cruise['time'].min()
    t_takeoff = df_takeOff['time'].max() - df_takeOff['time'].min()
    t_landing = df_landing['time'].max() - df_landing['time'].min()
    distance = total_distance(df_cruise)

    altitude_takeoff = df_takeOff['z'].max() - df_takeOff['z'].min()
    altitude_landing = df_landing['z'].max() - df_landing['z'].min()
    e_measured_cruise = scipy.integrate.simps(df_cruise['Power'], x=df_cruise["time"], even="avg") / 3600
    e_measured_takeoff = scipy.integrate.simps(df_takeOff['Power'], x=df_takeOff["time"], even="avg") / 3600
    e_measured_landing = scipy.integrate.simps(df_landing['Power'], x=df_landing["time"], even="avg") / 3600

    energy_measured_total = e_measured_takeoff + e_measured_cruise + e_measured_landing

    return t_takeoff, t_cruise, t_landing, e_measured_takeoff, e_measured_cruise, e_measured_landing, distance, \
           altitude_takeoff, altitude_landing




def generateInflightComponents(df_log,flight):
    DataDirectory = '/Volumes/GoogleDrive/Shared drives/DOE EP/Data'

    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    payload = df_log['payload_[g]'][flight]
    m = payload / 1000 + 3.08 + 0.635
    rho = airdensity.AirDensity(df_log, flight)
    start_time = time.time()
    print("flight :", flight)

    flightfolder = DataDirectory + "/" + str(flight)
    os.chdir(flightfolder)
    df = pd.read_csv('combined.csv')

    takeOff, landing, cruise, wholeflight = FindingRegimeFilter.FindRegime(df)
    df = wholeflight
    df['phi'], df['theta'], df['psi'] = pwf.quaternion_to_euler(df)
    df['Power'] = df['battery_voltage'] * df['battery_current']
    df['T'] = pwf.Thrust(m, gravity, df['phi'], df['theta'])
    df['Vbi'], df['Vbj'], df['Vbk'] = pwf.VairBody(df)
    df['v_i'] = inducedVelocity.CalculateVi(df, rho, A)
    df['alpha'] = 90 - df['theta']
    df['beta'] = df['phi']
    df['Pi_Estimated'] = pwf.InducedPower(df)

    df_copy = df.copy()
    df_copy['phi'], df_copy['theta'] = df['phi'] * 0, df['theta'] * 0
    df_copy['T'] = pwf.Thrust(m, gravity, df_copy['phi'], df_copy['theta'])
    df_copy['Vbi'], df_copy['Vbj'], df_copy['Vbk'] = df['Vbi'] * 0, df['Vbj'] * 0, df['Vbk'] * 0
    df_copy['alpha'] = df_copy['theta'] * 0 + np.pi / 2
    df_copy['beta'] = df['beta'] * 0
    df_copy['v_i'] = inducedVelocity.CalculateVi(df_copy, rho, A)
    df['Pi_hover'] = pwf.InducedPower(df_copy)

    os.chdir('/Users/thiagorodrigues/Box/Thiago DOE Research/Delivery Robots/First Principles/Energy_Model/flights')
    df.to_csv('%d.csv' % (flight))
    print("--- flight %d: %.2f seconds ---" % (flight, float(time.time() - start_time)))
    return(df)


def main():
    '''
    This script adds the euler angles, power, air speed velocities (no wind condition), thrust, alpha and beta angles,
    induced velocity, induced power and theoretical induced hover power.
    :return: a dataframe for each flight with all the components described above.
    '''
    mainpath = os.getcwd()
    DataDirectory = '/Volumes/GoogleDrive/Shared drives/DOE EP/Data (1)'
    os.chdir(DataDirectory)
    df_log = fix.FixColumns(pd.read_csv('FlightSheet.csv'))

    df_log = df_log[df_log['data_acquired']== 'yes']

    index = df_log.index.values

    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    parameters = []
    for flight in index:

        payload = df_log['payload_[g]'][flight]
        m = payload/1000 + 3.08 + 0.635
        speed = int(df_log['speed_[m/s]'][flight])
        altitude = int(df_log['altitude_[m]'][flight])
        #print(flight)
        rho = airdensity.AirDensity(df_log, flight)
        start_time = time.time()
        print("flight :",flight)


        flightfolder = DataDirectory + "/" + str(flight)
        os.chdir(flightfolder)
        df = pd.read_csv('combined.csv')

        takeOff, landing, cruise, wholeflight = FindingRegimeFilter.FindRegime(df)
        df = wholeflight
        df['phi'], df['theta'], df['psi'] = pwf.quaternion_to_euler(df)
        df['Power'] = df['battery_voltage'] * df['battery_current']
        df['T'] = pwf.Thrust(m, gravity, df['phi'], df['theta'])
        df['Vbi'], df['Vbj'], df['Vbk'] = pwf.VairBody(df)
        df['v_i'] = inducedVelocity.CalculateVi(df, rho, A)
        df['alpha'] = 90 - df['theta']
        df['beta'] = df['phi']
        df['Pi_Estimated'] = pwf.InducedPower(df)

        df_copy = df.copy()
        df_copy['phi'], df_copy['theta'] = df['phi']*0, df['theta']*0
        df_copy['T'] = pwf.Thrust(m, gravity, df_copy['phi'], df_copy['theta'])
        df_copy['Vbi'], df_copy['Vbj'], df_copy['Vbk'] = df['Vbi']*0, df['Vbj']*0, df['Vbk']*0
        df_copy['alpha'] = df_copy['theta'] * 0 + np.pi / 2
        df_copy['beta'] = df['beta']*0
        df_copy['v_i'] = inducedVelocity.CalculateVi(df_copy, rho, A)
        df['Pi_hover'] = pwf.InducedPower(df_copy)

        os.chdir('/Users/thiagorodrigues/Box Sync/Thiago DOE Research/Delivery Robots/First '
                 'Principles/Energy_Model/flights')
        df.to_csv('%d.csv'%(flight))
        print("--- flight %d: %.2f seconds ---" % (flight,float(time.time() - start_time)))


if __name__ == '__main__':
    main()
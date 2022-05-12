import pandas as pd
import datetime
import METAR_KAGC
import numpy as np
import os
   

def CreateCsv(df):
    '''
    this function creates a csv file with the number of the flight and the estimated air density.
    This process takes a few seconds perf flight, so it is better to do it only once and then use the results from the csv
    for one flight use the function AirDensity
    :param df: [DataFrame] data frame with all the flights 'FlightSheet.csv'
    :param mainpath: [str] where the csv file will be created
    :return: csv file with the number of the flight and the estimated air density
    '''
    df['date'] = df['date'] + ' '
    df['time_day'] = df['time_day'] + ':00.0'
    df['date'] = df['date'].astype(str)
    df['time_day']= df['time_day'].astype(str)
    df['time'] = df[['date','time_day']].apply(lambda x: ''.join(x), axis=1)

    print('colecting airdensity values')

    rho = []
    wind = []
    flights = list(set(df.flight))
    for flight in flights:
        print(flight)
        sub_df = df[df.flight == flight]
        date_time_obj = datetime.datetime.strptime(sub_df.time.max(),'%Y-%m-%d %H:%M:%S.%f')
        rho_flight = METAR_KAGC.calculate_density(date_time_obj)
        print(rho_flight)
        wind_max = METAR_KAGC.calculate_wind_speed(date_time_obj)

        rho.append(rho_flight)
        wind.append(wind_max)
        print("flight: %d, rho: %f kg/m3, wind: %.2f knots"%(flight, rho_flight, wind_max))
    print(rho)

    airdensity = pd.DataFrame({"flight":flights, 'rho':rho, "wind":wind})
    airdensity.to_csv("airdensity.csv")



def AirDensity(df_log):
    '''
    This function returns the air density for a particular flight
    :param df: [DataFrame] data frame with all the flights 'FlightSheet.csv'
    :param flight: [int] flight number
    :return: [float] air density in [kg/m^3]
    '''
    df = df_log.copy()
    df['date'] = df['date'] + ' '
    df['time_day'] = df['time_day'] + ':00.0'
    df['date'] = df['date'].astype(str)
    df['time_day'] = df['time_day'].astype(str)
    df['time_day'] = df[['date', 'time_day']].apply(lambda x: ''.join(x), axis=1)

    date_time_obj = datetime.datetime.strptime(df['time_day'].min(), '%Y-%m-%d %H:%M:%S.%f')
    rho = METAR_KAGC.calculate_density(date_time_obj)
    return rho

def AirDensityForIndex(df_log):
    '''
    This function returns the air density for a list of flights
    :param df: [DataFrame] data frame with all the flights 'FlightSheet.csv'
    :param flight: [int] flight number
    :return: [series] air density in [kg/m^3]
    '''
    df = df_log.copy()
    df['date_[yyyy-mm-dd]'] = df['date_[yyyy-mm-dd]'] + ' '
    df['time_[hh:mm]'] = df['time_[hh:mm]'] + ':00.0'
    df['date_[yyyy-mm-dd]'] = df['date_[yyyy-mm-dd]'].astype(str)
    df['time_[hh:mm]']= df['time_[hh:mm]'].astype(str)
    df['time'] = df[['date_[yyyy-mm-dd]','time_[hh:mm]']].apply(lambda x: ''.join(x), axis=1)

    rho = []
    print('colecting airdensity values')
    for flight in list(df.index.values):
        print('flight:', flight)
        date_time_obj = datetime.datetime.strptime(df['time'][flight],'%Y-%m-%d %H:%M:%S.%f')
        rho.append(METAR_KAGC.calculate_density(date_time_obj))
    return rho

def main():
    data = pd.read_csv("flights.csv")
    CreateCsv(data)


if __name__ == "__main__":
    main()
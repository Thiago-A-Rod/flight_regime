import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy.integrate
import scipy.ndimage
import seaborn as sns
import time


def Filter(df):
    '''
    this function creates a gaussian filter that smooths the altitude-time relation
    :param df: [DataFrame] the flight data frame
    :return: [series] the altitude filtered
    '''
    altitude = df["position_z"]
    sigma = 5
    filtered = scipy.ndimage.filters.gaussian_filter(altitude, sigma)
    plt.plot(df['time'],altitude, linewidth=1, label="Original data")
    plt.plot(df["time"],filtered, linewidth=1, label="Filtered data")
    plt.xlim(40, 60)
    plt.ylim(64, 78)
    sns.despine(top=True, right=True)
    plt.grid(which="major", color='gray', alpha=0.1)
    plt.xlabel("Time [s]", fontsize=14)
    plt.ylabel("Altitude [m]", fontsize=14)
    plt.scatter(df.loc[315,'time'],df.loc[315,'position_z']+0.1, c='black', s=10)
    plt.text(df.loc[315,'time']-0.2,df.loc[315,'position_z']+0.3,"B", c='black')
    plt.legend(frameon=False, loc="lower right")
    plt.savefig("figureS2.png")
    plt.show()
    return filtered


def Slopes(filteredData):  # finds the slopes (first derivative)
    '''
    this function finds the slopes through the first derivative of the filtered altitude
    :param filteredData: [series] the altitude filtered
    :return: slopes [series] the first derivative of the filtered altitude; [float] the index of the starting and finishing
    points of take-off, cruise and landing.
    '''
    slopes = list(np.diff(filteredData))
    #plt.plot(slopes)
    #plt.show()
    maxSlope = max(slopes)
    minSlope = min(slopes)
    indexMax = slopes.index(maxSlope)
    indexMin = slopes.index(minSlope)
    takeOffStartIndex = 0
    while slopes[takeOffStartIndex] <= 0.05:
        takeOffStartIndex += 1
    takeOffFinishIndex = indexMax
    while slopes[takeOffFinishIndex] > 0:
        takeOffFinishIndex += 1

    landFinishIndex = indexMin
    while (landFinishIndex < (len(slopes) - 1)) and (slopes[landFinishIndex] < -0.025):
        landFinishIndex += 1
    landStartIndex = indexMin
    while (slopes[landStartIndex] < 0):
        landStartIndex -= 1

    return slopes, takeOffStartIndex, takeOffFinishIndex, landStartIndex, landFinishIndex


def find_regime(df):
    '''
    this function divides the data frame in takeoff, landing, cruise and wholeflight regimes
    :param df: [DataFrame] the flight data frame
    :return: [DataFrame] of the portion of the flight corresponding to takeoff, landing, cruise and wholeflight regimes
    '''
    df = df.reset_index()
    df["position_z"] = df["position_z"] - pd.DataFrame.min(df["position_z"])
    filtered = Filter(df)
    slopes, takeOffStartIndex, takeOffFinishIndex, landStartIndex, landFinishIndex = Slopes(filtered)
    print("B:",takeOffFinishIndex)
    TKStart = df["time"][takeOffStartIndex]
    TKfinish = df["time"][takeOffFinishIndex]
    LANDStart = df["time"][landStartIndex]
    LANDFinish = df["time"][landFinishIndex]
    takeOff = df[(df.time < TKfinish) & (df.time > TKStart)].copy()
    takeOff.loc[:, 'regime'] = 'takeoff'
    landing = df[(df.time > LANDStart) & (df.time < LANDFinish)].copy()
    landing.loc[:, 'regime'] = 'landing'
    cruise = df[(df.time > TKfinish) & (df.time < LANDStart)].copy()
    cruise.loc[:, 'regime'] = 'cruise'
    wholeflight = df[(df.time > TKStart) & (df.time < LANDFinish)].copy()
    sigma = 5

    #filtered = scipy.ndimage.filters.gaussian_filter(landing['position_z'], sigma)
    #slopes = list(np.diff(filtered))

    
    #plt.plot(cruise['time'],cruise['position_z'])
    #plt.title("Flight: %d"%(df.flight.max()))
    #plt.show()
    #plt.plot(slopes)
    #plt.title("Flight: %d" % (df.flight.max()))
    #plt.show()
    
    
    return takeOff, landing, cruise, wholeflight

def main():
    data = pd.read_csv("flights.csv")
    for flight in [201]: #list(set(data.flight)):
        print('flight:', flight)
        df = data[data.flight == flight].copy()
        df = df.reset_index()
        df["position_z"] = df["position_z"] - pd.DataFrame.min(df["position_z"])
        filtered = Filter(df)
        slopes, takeOffStartIndex, takeOffFinishIndex, landStartIndex, landFinishIndex = Slopes(filtered)
        #plt.plot(df.time, df.position_z)
        #plt.title("Flight: %d" % (flight))
        #plt.savefig("%d.png"%(flight))
        #plt.show()
        takeOff, landing, cruise, wholeflight = find_regime(df)
        regimes = [takeOff, cruise, landing]
        plt.plot(takeOff['time'],takeOff['position_z'], label= "Takeoff")
        plt.plot(cruise['time'],cruise['position_z'], label="Cruise")
        plt.plot(landing['time'],landing['position_z'], label="Landing")
        sns.despine(top=True, right=True)
        plt.grid(which="major", color='gray', alpha=0.1)
        plt.xlabel("Time [s]", fontsize=14)
        plt.ylabel("Altitude [m]", fontsize=14)
        points = [takeOffStartIndex, takeOffFinishIndex, landStartIndex, landFinishIndex]
        labels = ["A", "B", "C", "D"]
        for i in range(len(labels)):
            plt.scatter(df.loc[points[i],'time'], df.loc[points[i],'position_z'] + 0.1, c='black', s=10)
            plt.text(df.loc[points[i],'time']-2.5, df.loc[points[i],'position_z']+2,labels[i], c='black')
        plt.legend(frameon=False, ncol=3)
        plt.savefig("figureS4.png")
        plt.show()



if __name__ == '__main__':
    main()


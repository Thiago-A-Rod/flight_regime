import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import os
import scipy.integrate
import scipy.ndimage
import seaborn as sns


def Filter(df):
	'''
	this function creates a gaussian filter that smooths the altitude-time relation
	:param df: [DataFrame] the flight data frame
	:return: [series] the altitude filtered
	'''
	altitude = df["position_z"]
	sigma = 5
	filtered = scipy.ndimage.filters.gaussian_filter(altitude,sigma)
	#plt.plot(df['time'],altitude)
	#plt.plot(df["time"],filtered)
	#plt.show()
	return filtered


def Slopes(filteredData): # finds the slopes (first derivative)
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
	while (landFinishIndex < (len(slopes)-1)) and (slopes[landFinishIndex] < 0):
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
	filtered= Filter(df)
	slopes, takeOffStartIndex, takeOffFinishIndex, landStartIndex, landFinishIndex = Slopes(filtered)

	TKStart = df["time"][takeOffStartIndex]
	TKfinish = df["time"][takeOffFinishIndex]
	LANDStart = df["time"][landStartIndex]
	LANDFinish = df["time"][landFinishIndex]
	takeOff = df[(df.time < TKfinish) & (df.time > TKStart)].copy()
	takeOff.loc[:,'regime'] = 'takeoff'
	landing = df[(df.time > LANDStart) & (df.time < LANDFinish)].copy()
	landing.loc[:,'regime'] = 'landing'
	cruise = df[(df.time > TKfinish) & (df.time < LANDStart)].copy()
	cruise.loc[:,'regime'] = 'cruise'
	wholeflight = df[(df.time > TKStart) & (df.time < LANDFinish)].copy()
	return takeOff, landing, cruise, wholeflight


def main():
	instructions = '''
	This module provides a function that divide a flight data set in 3 flight regimes: takeoff, cruise, and landing.
	The data set must have a time stamp and a vertical (GPS) position state, named “time” and “position_z”, respectively. 
	The module assumes that the drone performs completely vertical takeoff and landing maneuvers, with relatively steady altitude during cruise.
	To use this module, call the function find_regime(df) with the flight data set in the argument. 
	The function returns four data frames for the takeoff, landing, cruise, and whole flight. 
	For instance:
	
	import pandas
	from FindingRegime import *

	df = pandas.read_csv("flight_data_set.csv")
	takeOff, landing, cruise, wholeflight = find_regime(df)   
	
	A collection of flight data set is available at https://doi.org/10.1184/R1/12683453
	For more information on the data collection, refer to Rodrigues, et. al. (2021) at https://www.nature.com/articles/s41597-021-00930-x 
	'''
	print(instructions)


if __name__ == '__main__':
	main()


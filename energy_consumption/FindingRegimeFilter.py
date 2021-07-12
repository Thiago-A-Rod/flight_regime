import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import os
import scipy.integrate
import scipy.ndimage
import seaborn as sns


def Filter(df):
	'''
	this function adds a gaussian filter that smooths the altitude-time relation
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

def FindRegime(df):
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
	'''
	This function creates Supplementary Figures S1 to S4
	:return:
	'''

	plt.rcParams.update({'figure.autolayout': True})
	plt.rcParams["font.family"] = "Helvetica"
	plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})

	data = pd.read_csv('flights.csv')
	for flight in [201]:
		print(flight)
		df = data[data['flight'] == flight]
		df = df.reset_index()
		df["position_z"] = df["position_z"] - pd.DataFrame.min(df["position_z"])
		df['Power'] = df['battery_current']*df['battery_voltage']
		takeOff, landing, cruise, wholeflight = FindRegime(df)
		limits_x = [takeOff['time'].iloc[0], takeOff['time'].iloc[-1], cruise['time'].iloc[-1],
					landing['time'].iloc[-1]]
		limits_y = [takeOff['position_z'].iloc[0], takeOff['position_z'].iloc[-1], cruise['position_z'].iloc[-1],
					landing['position_z'].iloc[-1]]
		label_limits = ['A', 'B', 'C', 'D']


		fig, ax1 = plt.subplots(figsize=(10, 8))
		ax1.plot(df['time'], df['position_z'])
		filtered = Filter(df)
		ax1.plot(df['time'],filtered)
		ax1.set_xlabel('Time [s]', fontsize=20)
		ax1.set_ylabel('Altitude [m]', fontsize=20)

		sns.despine(top=True, right=True)
		ax1.grid(b=True, which='major', color='gray', linewidth=1.0, alpha=0.1)
		ax1.set_xlim([40, 60])
		ax1.set_ylim([64, 78])

		ax1.plot(limits_x[1], limits_y[1], marker='o', markersize=5, color='black')
		ax1.text(limits_x[1] - 0.2, limits_y[1]+0.2, label_limits[1], fontsize=16)
		ax1.set_xticklabels(ax1.get_xticks(), Fontsize=16)
		ax1.set_yticklabels(ax1.get_yticks(), Fontsize=16)
		plt.savefig('figureS2.png')
		plt.show()

		slopes, takeOffStartIndex, takeOffFinishIndex, landStartIndex, landFinishIndex = Slopes(filtered)
		fig, ax1 = plt.subplots(figsize=(10, 8))
		ax1.plot(df['time'], [0] + slopes)
		ax1.set_xlabel('Time [s]', fontsize=20)
		ax1.set_ylabel("Altitude's first derivative [m/s]", fontsize=20)
		slope_limit = [0.05, 0, 0, 0]
		for i in range(2):
			ax1.plot(limits_x[i], slope_limit[i], marker='o', markersize=5, color='black')
			ax1.text(limits_x[i] - 8, slope_limit[i]+0.02, label_limits[i], fontsize=16)
		for i in range(2,4):
			ax1.plot(limits_x[i], slope_limit[i], marker='o', markersize=5, color='black')
			ax1.text(limits_x[i] - 3, slope_limit[i]+0.02, label_limits[i], fontsize=16)
		sns.despine(top=True, right=True)
		ax1.grid(b=True, which='major', color='gray', linewidth=1.0, alpha=0.1)
		#ax1.set_xlim([40, 60])
		#ax1.set_ylim([64, 78])
		ax1.set_xticklabels(ax1.get_xticks(), Fontsize=16)
		ax1.set_yticklabels(np.round(ax1.get_yticks(),2), Fontsize=16)
		plt.savefig('figureS3.png')
		plt.show()

		fig, ax1 = plt.subplots(figsize=(10, 8))
		ax1.plot(takeOff['time'],takeOff["position_z"], label = "Take off")
		ax1.plot(cruise["time"], cruise["position_z"], label="Cruise")
		ax1.plot(landing["time"],landing["position_z"], label = "Landing")
		for i in range(len(limits_x)):
			ax1.plot(limits_x[i], limits_y[i], marker='o', markersize=5, color='black')
			ax1.text(limits_x[i] - 3, limits_y[i]+1, label_limits[i], fontsize=16)
		ax1.set_xlabel('Time [s]', fontsize=20)
		ax1.set_ylabel("Altitude's first derivative [m/s]", fontsize=20)

		sns.despine(top=True, right=True)
		ax1.grid(b=True, which='major', color='gray', linewidth=1.0, alpha=0.1)
		# ax1.set_xlim([40, 60])
		# ax1.set_ylim([64, 78])
		ax1.set_xticklabels(ax1.get_xticks(), Fontsize=16)
		ax1.set_yticklabels(np.round(ax1.get_yticks(), 2), Fontsize=16)
		plt.savefig('figureS4.png')
		plt.show()


		fig, ax1 = plt.subplots(figsize=(10, 8))
		ax1.plot(df['time'], df['position_z'])
		ax1.set_xlabel('Time [s]', fontsize=20)
		ax1.set_ylabel('Altitude [m]', fontsize=20)
		ax1.set_xticklabels(ax1.get_xticks(), Fontsize=16)
		ax1.set_yticklabels(ax1.get_yticks(), Fontsize=16)
		for i in range(len(limits_x)):
			ax1.plot(limits_x[i], limits_y[i], marker='o', markersize=5, color='black')
			ax1.text(limits_x[i] - 3, limits_y[i]+1, label_limits[i], fontsize=16)
		sns.despine(top=True, right=True)
		ax1.grid(b=True, which='major', color='gray', linewidth=1.0, alpha=0.1)
		plt.savefig('figureS1.png')
		plt.show()



if __name__ == '__main__':
	main()


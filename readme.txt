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
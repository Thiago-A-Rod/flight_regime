import pandas as pd
import numpy as np
import FindingRegime2
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.integrate


data = pd.read_csv("flights.csv")
flights = list(set(data.flight))

avg_power = []
for flight in flights: #range(205, 217):
    df = data[data.flight == flight].copy()
    df['power'] = np.fabs(df.battery_voltage*df.battery_current)
    energy = scipy.integrate.simps(df['power'], x=df["time"], even="avg") / 3600
    #plt.plot(df.time, df.power)
    #plt.show()
    avg_power.append(df.power.mean())
    print("Flight: %d, Ancillary Energy: %.8f Wh, Average Power: %.5f W"%(flight, energy, df.power.mean()))

print(np.mean(avg_power))

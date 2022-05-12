# This module calls all other modules.

import pandas as pd
import read_flights
import matplotlib.pyplot as plt
from calculate_energy import energy_two_way
import numpy as np
import seaborn as sns
from matplotlib import rcParams
import matplotlib.ticker as mtick
import LinearRegression as lr
import plot_deliveryDistances as pdd
import takeoff_energy
import FindingRegimeFilter as fd
import plot_regression_lines as prl

def main():
    pdd.figure1()


if __name__ == '__main__':
    main()

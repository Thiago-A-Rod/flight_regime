import pandas as pd
from calculate_energy import *


def takeoff_variation():
    coeff = pd.read_csv('coefficients_model1.csv', index_col=0)
    distance = 6.7
    #print(df)
    Energy_tk1_100, Energy_cr1_100, Energy_ld1_100, Energy_tk2_100, Energy_cr2_100, Energy_ld2_100 = \
        energy_split_two_way(distance, coeff, payload=1000, speed=12, altitude=100)
    Energy_tk1_5, Energy_cr1_5, Energy_ld1_5, Energy_tk2_5, Energy_cr2_5, Energy_ld2_5 = \
        energy_split_two_way(distance, coeff, payload=1000, speed=12, altitude=5)
    e_takeoff_100 = Energy_tk1_100 + Energy_tk2_100
    e_takeoff_5 = Energy_tk1_5 + Energy_tk2_5
    e_landing_100 = Energy_ld1_100 + Energy_ld2_100
    e_landing_5 = Energy_ld1_5 + Energy_ld2_5
    e_total_100 = Energy_tk1_100 + Energy_cr1_100 + Energy_ld1_100 + Energy_tk2_100 +\
                  Energy_cr2_100 + Energy_ld2_100
    e_total_5 = Energy_tk1_5 + Energy_cr1_5 + Energy_ld1_5 + Energy_tk2_5 + Energy_cr2_5 + Energy_ld2_5
    print("Total takeoff energy (100 m)", Energy_tk1_100 + Energy_tk2_100)
    print("Total takeoff energy (5 m)", Energy_tk1_5 + Energy_tk2_5)
    print("Total landing energy (100 m)", Energy_ld1_100 + Energy_ld2_100)
    print("Total landing energy (5 m)", Energy_ld1_5 + Energy_ld2_5)
    print('Total takeof + landing (100)', e_takeoff_100 + e_landing_100)
    print('Total takeof + landing (5)', e_takeoff_5 + e_landing_5)
    print('Share tk+ld (100)', (e_takeoff_100 + e_landing_100)/e_total_100)
    print('Share tk+ld (5)', (e_takeoff_5 + e_landing_5)/e_total_5)
    print('Total E (100)', e_total_100)
    print('Total E (5)', e_total_5)
    print('TK + LD Reduction BY', 1 - (e_takeoff_5 + e_landing_5)/(e_takeoff_100 + e_landing_100))
    print('Total Energy Reduction by', 1 - e_total_5/(e_total_100))
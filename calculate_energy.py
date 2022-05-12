import numpy as np


def energy_two_way(distance, coeff, payload=500, speed=12, altitude=100):
    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    m = 3.08 + 0.635
    rho = 1.20
    #Pi_unload = ((m * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)
    #Pi_load = (((m + payload / 1000) * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)
    Pi_unload = ((m ) ** (3 / 2)) / np.sqrt(rho)
    Pi_load = (((m + payload / 1000) ) ** (3 / 2)) / np.sqrt(rho)

    b1_tk = coeff.loc['takeoff', 'b1']
    b0_tk = coeff.loc['takeoff', 'b0']
    b1_cr = coeff.loc['cruise', 'b1']
    b0_cr = coeff.loc['cruise', 'b0']
    b1_ld = coeff.loc['landing', 'b1']
    b0_ld = coeff.loc['landing', 'b0']

    d = distance * 1000
    V = speed
    t = d/V
    takeoff_speed = 2.5
    landing_speed = 2.0
    Energy_tk1 = (Pi_load * b1_tk + b0_tk) * (altitude/takeoff_speed) / 3600 # Wh
    Energy_cr1 = (Pi_load * b1_cr + b0_cr) * t / 3600
    Energy_ld1 = (Pi_load * b1_ld + b0_ld) * (altitude/landing_speed) / 3600 # Wh
    Energy_tk2 = (Pi_unload * b1_tk + b0_tk) * (altitude/takeoff_speed) / 3600
    Energy_cr2 = (Pi_unload * b1_cr + b0_cr) * t / 3600
    Energy_ld2 = (Pi_unload * b1_ld + b0_ld) * (altitude/landing_speed) / 3600

    Total_Energy = Energy_tk1 + Energy_cr1 + Energy_ld1 + Energy_tk2 + Energy_cr2 + Energy_ld2
    return Total_Energy

def energy_one_way(distance, coeff, payload=500, speed=12, altitude = 100):
    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    m = 3.08 + 0.635 - 1
    rho = 1.20
    Pi_load = (((m + payload / 1000) * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)

    b1_tk = coeff.loc['takeoff', 'b1']
    b0_tk = coeff.loc['takeoff', 'b0']
    b1_cr = coeff.loc['cruise', 'b1']
    b0_cr = coeff.loc['cruise', 'b0']
    b1_ld = coeff.loc['landing', 'b1']
    b0_ld = coeff.loc['landing', 'b0']

    d = distance * 1000
    V = speed
    t = d / V

    Energy_tk1 = (Pi_load * b1_tk + b0_tk) * (altitude/2.5) / 3600  # assumes a 40 second takeoff
    Energy_cr1 = (Pi_load * b1_cr + b0_cr) * t / 3600
    Energy_ld1 = (Pi_load * b1_ld + b0_ld) * (altitude/2.0) / 3600  # assumes a 50 second landing

    Total_Energy = Energy_tk1 + Energy_cr1 + Energy_ld1
    return Total_Energy

def energy_split_two_way(distance, coeff, payload=500, speed=12, altitude=100):
    gravity = 9.81
    R = 0.15
    A = 4 * np.pi * R ** 2
    m = 3.08 + 0.635 - 1
    rho = 1.20
    Pi_unload = ((m * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)
    Pi_load = (((m + payload / 1000) * gravity) ** (3 / 2)) / np.sqrt(2 * rho * A)

    b1_tk = coeff.loc['takeoff', 'b1']
    b0_tk = coeff.loc['takeoff', 'b0']
    b1_cr = coeff.loc['cruise', 'b1']
    b0_cr = coeff.loc['cruise', 'b0']
    b1_ld = coeff.loc['landing', 'b1']
    b0_ld = coeff.loc['landing', 'b0']

    d = distance * 1000
    V = speed
    t = d / V
    takeoff_speed = 2.5
    landing_speed = 2.0
    Energy_tk1 = (Pi_load * b1_tk + b0_tk) * (altitude / takeoff_speed) / 3600  # assumes a 40 second takeoff
    Energy_cr1 = (Pi_load * b1_cr + b0_cr) * t / 3600
    Energy_ld1 = (Pi_load * b1_ld + b0_ld) * (altitude / landing_speed) / 3600  # assumes a 50 second landing
    Energy_tk2 = (Pi_unload * b1_tk + b0_tk) * (altitude / takeoff_speed) / 3600
    Energy_cr2 = (Pi_unload * b1_cr + b0_cr) * t / 3600
    Energy_ld2 = (Pi_unload * b1_ld + b0_ld) * (altitude / landing_speed) / 3600

    return Energy_tk1, Energy_cr1, Energy_ld1, Energy_tk2, Energy_cr2, Energy_ld2
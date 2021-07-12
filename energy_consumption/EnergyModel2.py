import pandas as pd
import numpy as np
import power_functions as pwf
import inducedVelocity
import scipy.integrate

def ModelTwo_validation(df, rho, A, m, gravity, c2,c3,c4,c5,c6,c7):
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

    duration = df['time'].max() - df['time'].min()
    emeasured = scipy.integrate.simps(df['Power'], x=df["time"], even="avg") / 3600
    df['Power_mean'] = df['Power'] * 0 + emeasured / duration

    # for Energy Model 2

    df['B1'] = df['Pi_Estimated']
    df['B2'] = rho * (df['T'] ** (3 / 2))
    df['B3'] = (df['Vbi'] ** 2 + df['Vbj'] ** 2) * rho * (df['T'] ** (1 / 2))
    df['B4'] = rho * (df['Vbi'] ** 3)
    df['B5'] = rho * (df['Vbj'] ** 3)
    df['B6'] = rho * (df['Vbk'] ** 3)

    df['PowerEstimated_Model2'] = df['B1'] + c2 * df['B2'] + c3 * df['B3'] + c4 * df['B4'] + c5 * df['B5'] + \
                                  c6 * df['B6'] + c7
    Energy_Measured = scipy.integrate.simps(df['Power'], x=df["time"], even="avg") / 3600
    Energy_Estimated = scipy.integrate.simps(df['PowerEstimated_Model2'], x=df["time"], even="avg") / 3600

    return Energy_Measured, Energy_Estimated

def validation(df):
    df['B1'] = df['Pi_Estimated']
    df['B2'] = (df['density'] * (df['T'] ** (3 / 2)))
    df['B3'] = (df['Vbi'] ** 2 + df['Vbj'] ** 2) * df['density'] * (df['T'] ** (1 / 2))
    df['B4'] = df['density'] * (df['Vbi'] ** 3)
    df['B5'] = df['density'] * (df['Vbj'] ** 3)
    df['B6'] = df['density'] * (df['Vbk'] ** 3)

    df['PowerEstimated_Model2'] = df['B1'] + df['c2'] * df['B2'] + df['c3'] * df['B3'] + df['c4'] * df['B4'] + df[
        'c5'] * df['B5'] +  df['c6'] * df['B6'] + df['c7']
    results = pd.DataFrame(columns=['flight','Energy_Measured','Energy_Estimated'])
    for flight in list(set(df['flight'])):
        print(flight)
        df1 = df[df['flight'] == flight]
        Energy_Measured = scipy.integrate.simps(df1['Power'], x=df1["time"], even="avg") / 3600
        Energy_Estimated = scipy.integrate.simps(df1['PowerEstimated_Model2'], x=df1["time"], even="avg") / 3600
        results = results.append({'flight':flight,'Energy_Measured':Energy_Measured,
                                  'Energy_Estimated':Energy_Estimated},ignore_index=True)

    return results

def calculatedInflightParameters_allflights(df):
    gravity = 9.81
    df['phi'], df['theta'], df['psi'] = pwf.quaternion_to_euler(df)
    df['Power'] = df['battery_voltage'] * df['battery_current']
    df['T'] = pwf.Thrust(df['m'], gravity, df['phi'], df['theta'])
    df['Vbi'], df['Vbj'], df['Vbk'] = pwf.VairBody(df)
    df['v_i'] = df.apply(inducedVelocity.vi, axis = 1)

    df['alpha'] = 90 - df['theta']
    df['beta'] = df['phi']
    df['Pi_Estimated'] = pwf.InducedPower(df)

    df_copy = df.copy()
    df_copy['phi'], df_copy['theta'] = df['phi'] * 0, df['theta'] * 0
    df_copy['T'] = pwf.Thrust(df['m'], gravity, df_copy['phi'], df_copy['theta'])
    df_copy['Vbi'], df_copy['Vbj'], df_copy['Vbk'] = df['Vbi'] * 0, df['Vbj'] * 0, df['Vbk'] * 0
    df_copy['alpha'] = df_copy['theta'] * 0 + np.pi / 2
    df_copy['beta'] = df['beta'] * 0
    df_copy['v_i'] = df_copy.apply(inducedVelocity.vi, axis = 1)
    df['Pi_hover'] = pwf.InducedPower(df_copy)
    return df

def findparameters(df):
    df['B1'] = df['Pi_Estimated']
    df['B2'] = (df['density'] * (df['T'] ** (3 / 2)))
    df['B3'] = (df['Vbi'] ** 2 + df['Vbj'] ** 2) * df['density'] * (df['T'] ** (1 / 2))
    df['B4'] = df['density'] * (df['Vbi'] ** 3)
    df['B5'] = df['density'] * (df['Vbj'] ** 3)
    df['B6'] = df['density'] * (df['Vbk'] ** 3)

    b = df['Power'] - df['B1']
    B7 = np.array([1 for i in range(len(df['B1']))])
    M = np.asarray([df['B2'], df['B3'], df['B4'], df['B5'], df['B6'], B7], dtype='float')
    print(M.shape)
    M = M.reshape(M.shape[1], M.shape[0])

    G = (-1) * np.eye(6)
    h = np.zeros((6, 1))
    P = np.dot(M.T, M)
    P = P.astype(np.double)

    q = -np.dot(M.T, b)
    q = q.astype(np.double)

    C = pwf.cvxopt_solve_qp(P, q, G, h)
    # c1 = float(C[0])
    c2 = float(C[0])
    c3 = float(C[1])
    c4 = float(C[2])
    c5 = float(C[3])
    c6 = float(C[4])
    c7 = float(C[5])

    df['PowerEstimated_Model2'] = df['B1'] + c2 * df['B2'] + c3 * df['B3'] + c4 * df['B4'] + c5 * df['B5'] + \
                                  c6 * df['B6'] + c7

    parameters = [c2,c3,c4,c5,c6,c7]

    return parameters



def CalculatedInflightParameters(df,rho, A, m, gravity, flight):
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

    duration = df['time'].max() - df['time'].min()
    emeasured = scipy.integrate.simps(df['Power'], x=df["time"], even="avg") / 3600
    df['Power_mean'] = df['Power'] * 0 + emeasured / duration

    # for Energy Model 2

    df['B1'] = df['Pi_Estimated']
    df['B2'] = rho * (df['T'] ** (3 / 2))
    df['B3'] = (df['Vbi'] ** 2 + df['Vbj'] ** 2) * rho * (df['T'] ** (1 / 2))
    df['B4'] = rho * (df['Vbi'] ** 3)
    df['B5'] = rho * (df['Vbj'] ** 3)
    df['B6'] = rho * (df['Vbk'] ** 3)

    b = df['Power'] - df['B1']
    B7 = np.array([1 for i in range(len(df['B1']))])
    M = np.asarray([df['B2'], df['B3'], df['B4'], df['B5'], df['B6'], B7], dtype='float')
    print(M.shape)
    M = M.reshape(M.shape[1], M.shape[0])
    G = (-1) * np.eye(6)
    h = np.zeros((6, 1))
    P = np.dot(M.T, M)
    P = P.astype(np.double)

    q = -np.dot(M.T, b)
    q = q.astype(np.double)

    C = pwf.cvxopt_solve_qp(P, q, G, h)
    #c1 = float(C[0])
    c2 = float(C[0])
    c3 = float(C[1])
    c4 = float(C[2])
    c5 = float(C[3])
    c6 = float(C[4])
    c7 = float(C[5])

    df['PowerEstimated_Model2'] = df['B1'] + c2 * df['B2'] + c3 * df['B3'] + c4 * df['B4'] + c5 * df['B5'] + \
                                  c6 * df['B6'] + c7

    parameters = np.array([flight, c2, c3, c4, c5, c6, c7])

    return parameters, df


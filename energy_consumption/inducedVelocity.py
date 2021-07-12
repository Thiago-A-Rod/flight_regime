import numpy as np
import pandas as pd
import os
import progressbar
import matplotlib.pyplot as plt
import time


def vi(row):
    T = row['T']
    A = row['A']
    rho = row['density']
    Vbi = row['Vbi']
    Vbj = row['Vbj']
    Vbk = row['Vbk']
    v_i = 0.00001
    w = - v_i + T / (2 * rho * A * np.sqrt(Vbi ** 2 + Vbj ** 2 + (Vbk + v_i) ** 2))
    step = 5
    while abs(w) > 0.001:
        while w > 0:
            v_i += step
            w = - v_i + T / (2 * rho * A * np.sqrt(Vbi ** 2 + Vbj ** 2 + (Vbk + v_i) ** 2))
        while w < 0:
            step = step/2
            v_i -= 2*step
            w = - v_i + T / (2 * rho * A * np.sqrt(Vbi ** 2 + Vbj ** 2 + (Vbk + v_i) ** 2))
    return v_i


def CalculateVi(df, rho, A):
    start_time = time.time()
    T = df['T']
    Vbi = df['Vbi']
    Vbj = df['Vbj']
    Vbk = df['Vbk']
    df['v_i'] = df.apply(vi,axis = 0,raw=True,args=(T,rho,A,Vbi,Vbj,Vbk))
    print('foi')

    counter = 0
    bar = progressbar.ProgressBar(maxval = 1,widgets=[progressbar.Bar('*', '[', ']'), ' ', progressbar.Percentage()] )
    bar.start()
    for i in list(df.index.values):
        bar.update(counter/len(list(df.index.values)))
        df['v_i'][i] = vi(T[i],rho,A,Vbi[i],Vbj[i],Vbk[i],counter)
        counter += 1
    bar.finish()
    print("--- %.2f seconds ---" % float(time.time() - start_time))


    return df['v_i']







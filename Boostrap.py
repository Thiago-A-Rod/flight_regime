import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import FindingRegimeFilter
import scipy.integrate
import inflightcomponents as inflight
import matplotlib.ticker as mtick
import LinearRegression as lr
import FindingRegime2
import airdensity
import model_one
from matplotlib.ticker import FormatStrFormatter


def rl(regime,interval,coeff):
    return [coeff.loc[regime,'b1']*interval[0] + coeff.loc[regime,'b0'],
            coeff.loc[regime,'b1']*interval[1] + coeff.loc[regime,'b0']]

def main():
    plt.rcParams.update({'figure.autolayout': True})
    plt.rcParams["font.family"] = "Helvetica"
    plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    plt.rcParams['legend.title_fontsize'] = 'large'

    mainpath = os.getcwd()
    #os.chdir(r'C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Data\Review\data\Kilthub')
    #data = pd.read_csv('flights.csv', low_memory=False)

    #data = data[((data.route == 'R1') | (data.route == 'R2') | (data.route == 'R3') | (data.route == 'R4') | (
    #            data.route == 'R5')) & (
    #                    data.payload < 750)]

    #data['Power'] = data['battery_current'] * data['battery_voltage']

    os.chdir(mainpath)

    summary = pd.read_csv('energy_summary_model1.csv')
    pool = pd.read_csv('pool.csv')
    tk_b1 = []
    tk_b0 = []
    cr_b1 = []
    cr_b0 = []
    ld_b1 = []
    ld_b0 = []

    os.chdir(r'C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Paper\energy_model\bootstrap')
    std = pd.DataFrame()
    n=2000
    fig, ax = plt.subplots()
    for i in range(n):
        print("iteration: %d"%(i), end='\r')
        subpool = np.random.choice(pool.flight, size=120, replace=True)
        summary.payload = summary.payload.astype(int)
        summary_pool = summary[summary.flight.isin(subpool)].copy()

        coeff = lr.linear_regression(summary_pool)
        tk_b1.append(coeff.loc['takeoff', 'b1'])
        tk_b0.append(coeff.loc['takeoff', 'b0'])
        cr_b1.append(coeff.loc['cruise', 'b1'])
        cr_b0.append(coeff.loc['cruise', 'b0'])
        ld_b1.append(coeff.loc['landing', 'b1'])
        ld_b0.append(coeff.loc['landing', 'b0'])

        local = pd.DataFrame({"iteration":i, "tk_b1":np.std(tk_b1), "tk_b0":np.std(tk_b0), "cr_b1":np.std(cr_b1),
                              "cr_b0":np.std(cr_b0), "ld_b1":np.std(ld_b1), "ld_b0":np.std(ld_b0)}, index=[0])

        std = pd.concat([std,local], ignore_index=True)


        interval = [0, 0.5]
        ax.plot(interval, rl('takeoff', interval, coeff), linestyle='--', color='black', alpha=0.7)
        #ax.plot(interval, rl('cruise', df, coeff), linestyle='--', color='black', alpha=0.7)
        #ax.plot(interval, rl('landing', df, coeff), linestyle='--', color='black', alpha=0.7)

    #plt.legend(title='Flight regime', frameon=False, loc="lower center", fontsize='large', ncol=3)
    #plt.ylim(500, 600)
    plt.xlim(interval)
    plt.xlabel(r"$\dfrac{mass^{1.5}}{\sqrt{\rho}}$ [$kg \cdot m^{1.5}$]", fontsize=20)
    plt.ylabel("Average Power [W]", fontsize=20)
    plt.xticks(fontsize=16)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.yticks(fontsize=16)
    sns.despine(top=True, right=True)
    plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
    #plt.savefig('Power_regime_trendline.pdf')
    plt.show()



    bootstrap = pd.DataFrame({"iteration":range(n),"tk_b1":tk_b1, "tk_b0":tk_b0, "cr_b1":cr_b1, "cr_b0":cr_b0, "ld_b1":ld_b1, "ld_b0":ld_b0})


    cols_b1 = ["tk_b1", "cr_b1", "ld_b1"]
    cols_b0 = ["tk_b0", "cr_b0", "ld_b0"]
    print(bootstrap)
    print(std)
    for col in cols_b1:
        plt.plot(std.iteration,std[col], label=str(col))
    plt.legend()
    plt.title("b1")
    plt.show()

    for col in cols_b0:
        plt.plot(std.iteration,std[col], label=str(col))
    plt.legend()
    plt.title("b0")
    plt.show()
    bootstrap.to_csv("bootstrap_results.csv", index=False)







if __name__ == "__main__":
    main()
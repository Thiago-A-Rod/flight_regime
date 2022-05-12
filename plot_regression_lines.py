import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.ticker import FormatStrFormatter

def rl(regime,df,coeff):
    return [coeff.loc[regime,'b1']*df.Pi_hover.min() + coeff.loc[regime,'b0'],
            coeff.loc[regime,'b1']*df.Pi_hover.max() + coeff.loc[regime,'b0']]


def plot_regression_regimes():
    plt.rcParams.update({'figure.autolayout': True})
    plt.rcParams["font.family"] = "Helvetica"
    plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    plt.rcParams['legend.title_fontsize'] = 'large'

    coeff = pd.read_csv('coefficients_model1.csv', index_col=0)
    df = pd.read_csv('energy_summary_model1.csv')
    #print(df)

    fig, ax = plt.subplots()
    ax.scatter(x=df['Pi_hover'], y=df['Power_takeoff'], label='Takeoff', alpha=0.5, color='blue')
    ax.scatter(x=df['Pi_hover'], y=df['Power_cruise'], label='Cruise', alpha=0.5, color='red')
    ax.scatter(x=df['Pi_hover'], y=df['Power_landing'], label='Landing', alpha=0.5, color='orange')
    interval=[260,330]
    ax.plot(interval, rl('takeoff',df,coeff), linestyle='--', color='black', alpha=0.7)
    ax.plot(interval, rl('cruise', df, coeff), linestyle='--', color='black', alpha=0.7)
    ax.plot(interval, rl('landing', df, coeff), linestyle='--', color='black', alpha=0.7)

    plt.legend(title='Flight regime', frameon=False, loc="lower center", fontsize='large', ncol=3)
    plt.ylim(0,750)
    #plt.xlim(interval)
    #plt.xlabel(r"$\dfrac{mass^{1.5}}{\sqrt{\rho}}$ [$kg \cdot m^{1.5}$]", fontsize=20)
    plt.xlabel(r"Induced Power [W]", fontsize=20)
    plt.ylabel("Average Power [W]", fontsize=20)
    plt.xticks(fontsize=16)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.yticks(fontsize=16)
    sns.despine(top=True, right=True)
    plt.grid(b=True, which='major', axis='both', color='gray', linewidth=1.0, alpha=0.1)
    plt.savefig('Power_regime_trendline.pdf')
    plt.show()


def main():
    plot_regression_regimes()


if __name__ == "__main__":
    main()
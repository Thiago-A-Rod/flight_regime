import pandas as pd
import numpy as np
import EnergyModel2
import matplotlib.pyplot as plt
import seaborn as sns
import add_regime


def main():
    try:
        df = pd.read_csv('inflights_merged.csv')
    except:
        try:
            df = pd.read_csv('flights_merged.csv')
        except:
            data = pd.read_csv('flights.csv', low_memory=False)
            data = data[((data.route == 'R1') | (data.route == 'R2') | (data.route == 'R3') | (data.route == 'R4') | (
                        data.route == 'R5')) & (data.payload < 750)]
            data['Power'] = data['battery_current'] * data['battery_voltage']
            add_regime.add_regime(data)
            df = pd.read_csv('flights_merged.csv')

        df['gravity'] = 9.81
        R = 0.15
        df['A'] = 4 * np.pi * R ** 2
        df['m'] = df['payload']/1000 + 3.08 + 0.635
        df = EnergyModel2.calculatedInflightParameters_allflights(df)
        df.to_csv('inflights_merged.csv')
        df = pd.read_csv('inflights_merged.csv')
    flight_index = list(set(df['flight']))
    print(flight_index)
    poll = np.random.choice(flight_index,120, replace=False)
    poll = pd.read_csv('poll.csv') # <-- poll of flights used in the paper
    df_120 = df[df.flight.isin(poll)]
    df_67 = df[~df['flight'].isin(poll)]

    # Bootstrap
    parameters = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    parameters_takeoff = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    parameters_cruise = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    parameters_landing = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    subpolls = pd.DataFrame()
    i = 0
    while i<= 1000:
        print(i)
        poll = np.array(poll).reshape(120)
        subpoll = np.random.choice(np.array(poll),120, replace=True)
        subpolls[i+1] = subpoll
        df_120 = pd.DataFrame(columns = df.columns)
        p = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
        p_takeoff = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
        p_cruise = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
        p_landing = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
        for flight in subpoll:
            df_120 = df[df['flight']==flight]
            df_120_takeoff = df_120[df_120['regime']=='takeoff']
            df_120_cruise = df_120[df_120['regime'] == 'cruise']
            df_120_landing = df_120[df_120['regime'] == 'landing']
            p.loc[i] = EnergyModel2.findparameters(df_120)
            p_takeoff.loc[i] = EnergyModel2.findparameters(df_120_takeoff)
            p_cruise.loc[i] = EnergyModel2.findparameters(df_120_cruise)
            p_landing.loc[i] = EnergyModel2.findparameters(df_120_landing)

        c2p = p['c2'].mean()
        c3p = p['c3'].mean()
        c4p = p['c4'].mean()
        c5p = p['c5'].mean()
        c6p = p['c6'].mean()
        c7p = p['c7'].mean()

        c2tk = p_takeoff['c2'].mean()
        c3tk = p_takeoff['c3'].mean()
        c4tk = p_takeoff['c4'].mean()
        c5tk = p_takeoff['c5'].mean()
        c6tk = p_takeoff['c6'].mean()
        c7tk = p_takeoff['c7'].mean()

        c2cr = p_cruise['c2'].mean()
        c3cr = p_cruise['c3'].mean()
        c4cr = p_cruise['c4'].mean()
        c5cr = p_cruise['c5'].mean()
        c6cr = p_cruise['c6'].mean()
        c7cr = p_cruise['c7'].mean()

        c2ld = p_landing['c2'].mean()
        c3ld = p_landing['c3'].mean()
        c4ld = p_landing['c4'].mean()
        c5ld = p_landing['c5'].mean()
        c6ld = p_landing['c6'].mean()
        c7ld = p_landing['c7'].mean()

        parameters.loc[i] = [c2p,c3p,c4p,c5p,c6p,c7p]
        parameters_takeoff.loc[i] = [c2tk,c3tk,c4tk,c5tk,c6tk,c7tk]
        parameters_cruise.loc[i] = [c2cr,c3cr,c4cr,c5cr,c6cr,c7cr]
        parameters_landing.loc[i] = [c2ld,c3ld,c4ld,c5ld,c6ld,c7ld]
        i += 1

    parameters['regime'] = 'whole'
    parameters_takeoff['regime'] = 'takeoff'
    parameters_cruise['regime'] =  'cruise'
    parameters_landing['regime'] = 'landing'

    parameters = parameters.append(parameters_takeoff, ignore_index=True)
    parameters = parameters.append(parameters_cruise, ignore_index=True)
    parameters = parameters.append(parameters_landing, ignore_index=True)
    parameters.to_csv('parameters_bootstrap.csv')
    subpolls.to_csv('subpolls_bootsrap.csv')


    parameters = pd.read_csv('parameters_bootstrap.csv')
    parameters_whole = parameters[parameters['regime']=='whole']
    parameters_takeoff = parameters[parameters['regime'] == 'takeoff']
    parameters_cruise = parameters[parameters['regime'] == 'cruise']
    parameters_landing = parameters[parameters['regime'] == 'landing']


    param = 'c2'
    sns.distplot(parameters_takeoff[param],hist = True, label = 'takeoff')
    sns.distplot(parameters_cruise[param], hist=True,label = 'cruise')
    sns.distplot(parameters_landing[param], hist=True,label = 'landing')
    plt.legend()
    #plt.show()


    print('%s & %.3f \\pm %.3f & %.3f \\pm %.3f & %.3f \\pm %.3f'%(param,
        parameters_takeoff[param].mean(),parameters_takeoff[param].std(),
        parameters_cruise[param].mean(),parameters_cruise[param].std(),
        parameters_landing[param].mean(),parameters_landing[param].std()))

    param = 'c3'
    sns.distplot(parameters_takeoff[param], hist=True, label='takeoff')
    sns.distplot(parameters_cruise[param], hist=True, label='cruise')
    sns.distplot(parameters_landing[param], hist=True, label='landing')
    plt.legend()
    #plt.show()
    print('%s & %.3f \\pm %.3f & %.3f \\pm %.3f & %.3f \\pm %.3f' % (param,
                                                                     parameters_takeoff[param].mean(),
                                                                     parameters_takeoff[param].std(),
                                                                     parameters_cruise[param].mean(),
                                                                     parameters_cruise[param].std(),
                                                                     parameters_landing[param].mean(),
                                                                     parameters_landing[param].std()))

    param = 'c4'
    sns.distplot(parameters_takeoff[param], hist=True, label='takeoff')
    sns.distplot(parameters_cruise[param], hist=True, label='cruise')
    sns.distplot(parameters_landing[param], hist=True, label='landing')
    plt.legend()
    #plt.show()
    print('%s & %.3f \\pm %.3f & %.3f \\pm %.3f & %.3f \\pm %.3f' % (param,
                                                                     parameters_takeoff[param].mean(),
                                                                     parameters_takeoff[param].std(),
                                                                     parameters_cruise[param].mean(),
                                                                     parameters_cruise[param].std(),
                                                                     parameters_landing[param].mean(),
                                                                     parameters_landing[param].std()))

    param = 'c5'
    sns.distplot(parameters_takeoff[param], hist=True, label='takeoff')
    sns.distplot(parameters_cruise[param], hist=True, label='cruise')
    sns.distplot(parameters_landing[param], hist=True, label='landing')
    plt.legend()
    #plt.show()
    print('%s & %.3f \\pm %.3f & %.3f \\pm %.3f & %.3f \\pm %.3f' % (param,
                                                                     parameters_takeoff[param].mean(),
                                                                     parameters_takeoff[param].std(),
                                                                     parameters_cruise[param].mean(),
                                                                     parameters_cruise[param].std(),
                                                                     parameters_landing[param].mean(),
                                                                     parameters_landing[param].std()))

    param = 'c6'
    sns.distplot(parameters_takeoff[param], hist=True, label='takeoff')
    sns.distplot(parameters_cruise[param], hist=True, label='cruise')
    sns.distplot(parameters_landing[param], hist=True, label='landing')
    plt.legend()
    #plt.show()
    print('%s & %.3f \\pm %.3f & %.3f \\pm %.3f & %.3f \\pm %.3f' % (param,
                                                                     parameters_takeoff[param].mean(),
                                                                     parameters_takeoff[param].std(),
                                                                     parameters_cruise[param].mean(),
                                                                     parameters_cruise[param].std(),
                                                                     parameters_landing[param].mean(),
                                                                     parameters_landing[param].std()))

    param = 'c7'
    sns.distplot(parameters_takeoff[param], hist=True, label='takeoff')
    sns.distplot(parameters_cruise[param], hist=True, label='cruise')
    sns.distplot(parameters_landing[param], hist=True, label='landing')
    plt.legend()
    #plt.show()
    print('%s & %.3f \\pm %.3f & %.3f \\pm %.3f & %.3f \\pm %.3f' % (param,
                                                                     parameters_takeoff[param].mean(),
                                                                     parameters_takeoff[param].std(),
                                                                     parameters_cruise[param].mean(),
                                                                     parameters_cruise[param].std(),
                                                                     parameters_landing[param].mean(),
                                                                     parameters_landing[param].std()))

    p = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    p_takeoff = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    p_cruise = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    p_landing = pd.DataFrame(columns=['c2', 'c3', 'c4', 'c5', 'c6', 'c7'])
    i = 0
    for flight in poll:
        df_120 = df[df['flight'] == flight]

        df_120_takeoff = df_120[df_120['regime'] == 'takeoff']
        df_120_cruise = df_120[df_120['regime'] == 'cruise']
        df_120_landing = df_120[df_120['regime'] == 'landing']
        print(i)

        p.loc[i] = EnergyModel2.findparameters(df_120)
        p_takeoff.loc[i] = EnergyModel2.findparameters(df_120_takeoff)
        p_cruise.loc[i] = EnergyModel2.findparameters(df_120_cruise)
        p_landing.loc[i] = EnergyModel2.findparameters(df_120_landing)
        i += 1

    c2p = p['c2'].mean()
    c3p = p['c3'].mean()
    c4p = p['c4'].mean()
    c5p = p['c5'].mean()
    c6p = p['c6'].mean()
    c7p = p['c7'].mean()

    c2tk = p_takeoff['c2'].mean()
    c3tk = p_takeoff['c3'].mean()
    c4tk = p_takeoff['c4'].mean()
    c5tk = p_takeoff['c5'].mean()
    c6tk = p_takeoff['c6'].mean()
    c7tk = p_takeoff['c7'].mean()

    c2cr = p_cruise['c2'].mean()
    c3cr = p_cruise['c3'].mean()
    c4cr = p_cruise['c4'].mean()
    c5cr = p_cruise['c5'].mean()
    c6cr = p_cruise['c6'].mean()
    c7cr = p_cruise['c7'].mean()

    c2ld = p_landing['c2'].mean()
    c3ld = p_landing['c3'].mean()
    c4ld = p_landing['c4'].mean()
    c5ld = p_landing['c5'].mean()
    c6ld = p_landing['c6'].mean()
    c7ld = p_landing['c7'].mean()

    parameters_final = pd.DataFrame()
    parameters_final['takeoff'] = [c2tk,c3tk,c4tk,c5tk,c6tk,c7tk]
    parameters_final['cruise'] = [c2cr,c3cr,c4cr,c5cr,c6cr,c7cr]
    parameters_final['landing'] = [c2ld,c3ld,c4ld,c5ld,c6ld,c7ld]
    parameters_final.to_csv('coefficient_summary_model2.csv')
    print(parameters_final)

    df_67['c2'], df_67['c3'], df_67['c4'], df_67['c5'], df_67['c6'], df_67['c7'] = 'NAN','NAN','NAN','NAN','NAN',"NAN"
    df_67['c2'][df_67['regime'] == 'takeoff'] = c2tk
    df_67['c3'][df_67['regime'] == 'takeoff'] = c3tk
    df_67['c4'][df_67['regime'] == 'takeoff'] = c4tk
    df_67['c5'][df_67['regime'] == 'takeoff'] = c5tk
    df_67['c6'][df_67['regime'] == 'takeoff'] = c6tk
    df_67['c7'][df_67['regime'] == 'takeoff'] = c7tk

    df_67['c2'][df_67['regime'] == 'cruise'] = c2cr
    df_67['c3'][df_67['regime'] == 'cruise'] = c3cr
    df_67['c4'][df_67['regime'] == 'cruise'] = c4cr
    df_67['c5'][df_67['regime'] == 'cruise'] = c5cr
    df_67['c6'][df_67['regime'] == 'cruise'] = c6cr
    df_67['c7'][df_67['regime'] == 'cruise'] = c7cr

    df_67['c2'][df_67['regime'] == 'landing'] = c2ld
    df_67['c3'][df_67['regime'] == 'landing'] = c3ld
    df_67['c4'][df_67['regime'] == 'landing'] = c4ld
    df_67['c5'][df_67['regime'] == 'landing'] = c5ld
    df_67['c6'][df_67['regime'] == 'landing'] = c6ld
    df_67['c7'][df_67['regime'] == 'landing'] = c7ld

    plt.show()

    energy_validation = EnergyModel2.validation(df_67)
    print(energy_validation)
    error = (energy_validation['Energy_Measured'] - energy_validation['Energy_Estimated']) / \
            energy_validation['Energy_Measured']
    error_summary_df = pd.DataFrame(error, columns=['model2'])
    error_summary_df.to_csv('error_summary_model_2.csv')
    print(error.mean())

    sns.distplot(error)
    plt.show()


if __name__ == '__main__':
    main()

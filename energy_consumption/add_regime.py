import FindingRegimeFilter as fd
import pandas as pd
import airdensity


def add_regime(data):
    df = pd.DataFrame([],columns=data.columns)
    print(df)
    for flight in list(set(data.flight)):
        print(flight)

        subdata = data[data.flight == flight]
        subdata['density'] = airdensity.AirDensity(subdata)
        takeOff, landing, cruise, wholeflight = fd.FindRegime(subdata)
        takeOff['regime'] = 'takeoff'
        landing['regime'] = 'landing'
        cruise['regime'] = 'cruise'
        df = df.append(takeOff, ignore_index=True)
        df = df.append(cruise, ignore_index=True)
        df = df.append(landing, ignore_index=True)
    df.drop(labels='index', axis=1, inplace=True)
    df.to_csv('flights_merged.csv', index=False)



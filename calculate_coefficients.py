# This module calls all other modules.

import pandas as pd
import LinearRegression as lr

def main():
    summary = pd.read_csv('Energy_summary_model1.csv')
    pool = pd.read_csv('pool.csv')
    summary.payload = summary.payload.astype(int)
    summary_pool = summary[summary.flight.isin(pool.flight)].copy()
    coeff = lr.linear_regression(summary_pool)
    coeff.to_csv('coefficients_model1.csv')


if __name__ == '__main__':
    main()

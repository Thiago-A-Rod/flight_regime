import numpy as np 
import pandas as pd
from scipy.stats import t
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib


def linear_regression(df):
	tk_x = df['Pi_hover']
	tk_y = df['Power_takeoff']

	cr_x = df['Pi_hover']
	cr_y = df['Power_cruise']

	ld_x = df['Pi_hover']
	ld_y = df['Power_landing']

	wl_x = df['Pi_hover']
	wl_y = df['avg_power']

	tk_b0, tk_b1, tk_pvalue, tk_Rsq = cal_coefficients(tk_x, tk_y)
	cr_b0, cr_b1, cr_pvalue, cr_Rsq = cal_coefficients(cr_x, cr_y)
	ld_b0, ld_b1, ld_pvalue, ld_Rsq = cal_coefficients(ld_x, ld_y)
	wl_b0, wl_b1, wl_pvalue, wl_Rsq = cal_coefficients(wl_x, wl_y)

	df_coefficients = pd.DataFrame([],columns = ['regime','b1','b0','p_value','R_sq'])
	df_coefficients.loc[0] = ['takeoff', tk_b1,tk_b0,tk_pvalue,tk_Rsq]
	df_coefficients.loc[1] = ['cruise', cr_b1, cr_b0, cr_pvalue, cr_Rsq]
	df_coefficients.loc[2] = ['landing', ld_b1, ld_b0, ld_pvalue, ld_Rsq]
	df_coefficients.loc[3] = ['total', wl_b1, wl_b0, wl_pvalue, wl_Rsq]

	df_coefficients.set_index('regime', inplace=True)
	df_coefficients.to_csv('coefficients_model1.csv')
	return df_coefficients


def cal_coefficients(x,y):
	xbar = x.mean()
	ybar = y.mean()
	n = len(x)
	Sxx = ((x - xbar)**2).sum()
	Sxy = ((x - xbar)*(y-ybar)).sum()


	b1 = Sxy/Sxx
	b0 = ybar - b1*xbar

	SStot = ((y - ybar)**2).sum()
	SSreg = b1**2 * Sxx
	SSerr = SStot - SSreg

	Rsq = SSreg/SStot
	s = np.sqrt(SSerr/(n-2))

	t_b1 = b1/(s/np.sqrt(Sxx))
	degF = n-2
	tcdf = t.cdf(t_b1, degF, loc=0, scale=1)
	#print(t_b1)
	if b1 < 0:
		pvalue = 2*(tcdf)
	else:
		pvalue = 2*(1-tcdf)

	return b0,b1,pvalue,Rsq


def estimate_energy(df_coef, Pi, times):
	regime = ['takeoff', 'cruise', 'landing']
	x = Pi
	energy = 0
	for reg in regime:
		b1 = df_coef['b1'][reg]
		b0 = df_coef['b0'][reg]
		time = times[reg]
		energy += EnergyEstimator(x,b0,b1,time)/3600
	return energy


def EnergyEstimator(x,b0,b1,time):
	return (b0+x*b1)*time


def EnergyMeasured(y,time):
	return y*time


def Error(Measured,Estimated):
	return (Measured - Estimated)/Measured



def main():
	df = pd.read_csv('power_ratios.csv')
	df_time = pd.read_csv('energy_ratios.csv')

	tk_x = df['pi_takeoff']
	tk_y = df['power_takeoff']
	tk_time = df_time['time_takeoff']

	cr_x = df['pi_cruise']
	cr_y = df['power_cruise']
	cr_time = df_time['time_cruise']

	ld_x = df['pi_landing']
	ld_y = df['power_landing']
	ld_time = df_time['time_landing']

	sns.scatterplot(x = tk_x,y = tk_y, label = 'take off')
	plt.title('Take Off')
	plt.xlabel('Induced Power (no wind, hover) [W]')
	plt.ylabel('Average Measured Power [W]')
	plt.show()

	sns.scatterplot(x=cr_x, y=cr_y, label='cruise')
	plt.title('Cruise')
	plt.xlabel('Induced Power (no wind, hover) [W]')
	plt.ylabel('Average Measured Power [W]')
	plt.show()

	sns.scatterplot(x=ld_x, y=ld_y, label='landing')
	plt.title('Landing')
	plt.xlabel('Induced Power (no wind, hover) [W]')
	plt.ylabel('Average Measured Power [W]')
	plt.show()

	tk_b0, tk_b1, tk_pvalue, tk_Rsq = Anova(tk_x,tk_y)
	cr_b0, cr_b1, cr_pvalue, cr_Rsq = Anova(cr_x, cr_y)
	ld_b0, ld_b1, ld_pvalue, ld_Rsq = Anova(ld_x, ld_y)

	print('take off',tk_b0, tk_b1, tk_pvalue, tk_Rsq)
	print('cruise',cr_b0, cr_b1, cr_pvalue, cr_Rsq)
	print('landing',ld_b0, ld_b1, ld_pvalue, ld_Rsq)
	#tk_time = cr_time = ld_time = 300

	model1Parameters = pd.DataFrame()
	model1Parameters['regime'] = ['takeoff','cruise','landing']
	model1Parameters['b0'] = [tk_b0,cr_b0,ld_b0]
	model1Parameters['b1'] = [tk_b1,cr_b1,ld_b1]
	model1Parameters.to_csv('Model1Parameters.csv')

	df['energy_takeoff'] = EnergyMeasured(tk_y,tk_time)
	df['energy_cruise'] = EnergyMeasured(cr_y, cr_time)
	df['energy_landing'] = EnergyMeasured(ld_y, ld_time)

	df['estimated_takeoff'] = EnergyEstimator(tk_x,tk_b0,tk_b1,tk_time)
	df['estimated_cruise'] = EnergyEstimator(cr_x, cr_b0, cr_b1, cr_time)
	df['estimated_landing'] = EnergyEstimator(ld_x, ld_b0, ld_b1, ld_time)
	df['Measured'] = df['energy_takeoff'] + df['energy_cruise'] + df['energy_landing']
	df['Estimated'] = df['estimated_takeoff'] + df['estimated_cruise'] + df['estimated_landing']
	df['error'] = Error(df['Measured'],df['Estimated'])
	'''
	fig = plt.figure()
	fig.set_size_inches(6, 4)
	axes = fig.add_axes([0.1, 0.2, sns.distplot(df['error'], hist=False, kde=True, kde_kws={'shade': True, 
																				'linewidth': 3}, ax=axes)0.8, 0.7])

	plt.title('Relative error of the energy estimation')
	fig.text(0, 0, 'Figure 1: Error between Measured and Estimated Energy Consumption',
			 verticalalignment='bottom',
			 horizontalalignment='left', fontsize=12)
	plt.show()
	'''
	alpha = 0.05
	df_out = df[(df['error'] <= -alpha) | (df['error'] >= alpha)]
	df_in = df[(df['error'] >= -alpha) & (df['error'] <= alpha)]
	totalflights = len(df['flight'])
	flightswithin = len(df_in['flight'])
	print('Total Flights =', totalflights)
	print('Flights within -%.2f < error < %.2f =' % (alpha, alpha), flightswithin)
	print('Percentage of Flight = {0:.0%}'.format(flightswithin / totalflights))
	print('Average Error = %.2f' % (df['error'].mean()))
	print('Stdev Error = %.2f' % (df['error'].std()))

	fig = plt.figure()
	fig.set_size_inches(6, 4)
	axes = fig.add_axes([0.1, 0.2, 0.8, 0.7])
	sns.scatterplot(x = 'Estimated', y= 'Measured', data = df_in, label = '|error| <= 5%', ax = axes)
	sns.scatterplot(x = 'Estimated', y= 'Measured', data = df_out, label = '|error| > 5%', ax = axes)
	plt.xlabel('Energy Estimated [Wh]')
	plt.ylabel('Energy Measured [Wh]')
	fig.text(0, 0, 'Figure 1 Measured and Estimated Energy Consumption',
			 verticalalignment='bottom',
			 horizontalalignment='left', fontsize=12)
	plt.show()

if __name__ == '__main__':
	main()
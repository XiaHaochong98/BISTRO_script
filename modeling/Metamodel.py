from Sample import *
from KPIS import *

import numpy
import scipy.optimize as optimization


def func(x, *p):
    social     =  p[0]*x[0] + p[1]*x[1] + p[2]*x[2] + p[3]*x[3]
    social += p[4]*x[0]*x[1] + p[5]*x[0]*x[2] + p[6]*x[0]*x[3] + p[7]*x[1]*x[2]
    social += p[8]*x[1]*x[3] + p[9] * x[2]*x[3]
    #congestion =  p[4]*x[0] + p[5]*x[1] + p[6]*x[2] + p[7]*x[3]
    return social


def fit_input_to_submission_score():
	samples = create_samples_list()
	standards = loadStandardization()

	xdata = []
	ydata = []

	for s in samples:
		
		x = s.road_pricing['x'] 
		y = s.road_pricing['y']
		r = s.road_pricing['r']
		p = s.road_pricing['p']

		social = computeWeightedScores(s, standards, social_KPI)[-1]
		#congestion = computeWeightedScores(s, standards, congestion_KPI)[-1]

		xdata.append([x,y,r,p])
		ydata.append(social)

	x0 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	xdata = np.array(xdata).transpose()
	ydata = np.array(ydata)


	optimum = optimization.curve_fit(func, xdata, ydata, x0)[0]
	print("optimum : ", optimum)
	print("MSE error : " + str(test(xdata.transpose(), ydata, optimum)))


def test(xi, yi, p):
	MSEloss = 0
	for x,y in zip(xi,yi):
		MSEloss += (func(x,*p) - y)**2
	return MSEloss/len(xi)


if __name__ == '__main__':
	fit_input_to_submission_score();
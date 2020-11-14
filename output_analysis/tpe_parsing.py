########################################################
"""

This script parses the output of the bistro hyperopt optimizater :



"""
########################################################
import os
import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys
sys.path.insert(1, '/home/ubuntu/Haochong_scripts')

TMV = "Congestion: total vehicle miles traveled"
AVG_DELAY = "Congestion: average vehicle delay per passenger trip"
WORK_BURDEN = "Equity: average travel cost burden - work"
BUS_CROWDING = "Level of service: average bus crowding experienced"
COSTS_BENEFITS = "Level of service: costs and benefits"
GHG = "Sustainability: Total grams GHGe Emissions"

SUBMISSION = "Submission Score"

#Get the current working directory
from utilities.navigate_data import *
from utilities.Sample import *
from utilities.collect_outputs import *
from utilities.collect_inputs import *
from fixed_data.KPIS import *

def graph_tpe_results(samples, standards, kpi = aggregate_KPI, name = "Aggregate"):
	plt.cla()
	results = [computeWeightedScores(s, standards, kpi)[-1] for s in samples]
	order = [i for i in range(len(results))]
	mini = [results[0]]+[min(results[:i]) for i in range(1, len(results))]
	
	plt.xlabel('Trial Number')
	plt.ylabel('Score')

	plt.plot(order, results, 'bo', label='TPE data points')
	plt.plot(order, mini, '--r', label='TPE progress')
	plt.legend(loc='upper right',frameon=True,framealpha=1.0)
	plt.savefig("tpe_score_evolution.png")

def graph_tpe_spread(samples, standards, kpi = aggregate_KPI, name = "Aggregate"):
	plt.cla()

	results = [computeWeightedScores(s, standards, kpi)[-1] for s in samples]
	order = [i for i in range(len(results))]
	mini = [results[0]]+[min(results[:i]) for i in range(1, len(results))]
	maxi = [results[0]]+[max(results[:i]) for i in range(1, len(results))]
	mean = [results[0]]+[np.mean(results[max(i-30,0):i]) for i in range(1, len(results))]
	med = [results[0]]+[np.median(results[max(i-30,0):i]) for i in range(1, len(results))]

	plt.plot(order, results, 'bo', alpha=0.2, label='TPE data points')
	plt.plot(order, mini, 'g', label='TPE min')
	plt.plot(order, maxi, 'r', label='TPE max')
	plt.plot(order, mean, 'm', label='TPE mean (last 30 its)')
	plt.plot(order, med, 'y', label='TPE median (last 30 its)')

	plt.xlabel('Trial Number')
	plt.ylabel('Score')

	plt.legend(loc='upper right',frameon=True,framealpha=1.0)

	plt.savefig(name+"_tpe_score_spread.png")



if __name__ == "__main__":
	samples = create_samples_list()
	standards = loadStandardization()
	graph_tpe_spread(samples, standards)

	graph_tpe_spread(samples, standards, TollRevenue_KPI, "Tolls")

	graph_tpe_spread(samples, standards, congestion_KPI, "Congestion")

	graph_tpe_spread(samples, standards, social_KPI, "Social")

	
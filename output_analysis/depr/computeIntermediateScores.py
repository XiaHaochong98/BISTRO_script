
import os
import sys
import csv
import matplotlib.pyplot as plt
import pandas as pd
import random


#rawScores.csv does not use the same KPI names as the fixed data files...
trans_dict = {

	'Iteration':'Iteration',

	'Accessibility: number of secondary locations accessible by car within 15 minutes':'driveSecondaryAccessibility',
	'Accessibility: number of secondary locations accessible by transit within 15 minutes':'transitSecondaryAccessibility',
	'Accessibility: number of work locations accessible by car within 15 minutes':'driveWorkAccessibility',
	'Accessibility: number of work locations accessible by transit within 15 minutes':'transitWorkAccessibility',

	'Congestion: average vehicle delay per passenger trip':'averageVehicleDelayPerPassengerTrip',
	'Congestion: total vehicle miles traveled':'motorizedVehicleMilesTraveled_total',
	'Equity: average travel cost burden -  secondary':'averageTravelCostBurden_Secondary',
	'Equity: average travel cost burden - work':'averageTravelCostBurden_Work',
	'Level of service: average bus crowding experienced':'busCrowding',
	'Level of service: costs and benefits':'costBenefitAnalysis',

	'Sustainability: Total grams GHGe Emissions':'sustainability_GHG',
	'Sustainability: Total grams PM 2.5 Emitted':'sustainability_PM'
}


#Get the current working directory
def get_dir():
	return os.getcwd()

#Get only subdir
def only_subdir(current_dir = os.getcwd()):
	return next(os.walk(current_dir))[1][0]

#Get a list of all subdirectories
def sub_list(current_dir = os.getcwd()):
	return [dir for dir in next(os.walk(current_dir))[1] if dir[0]=='5']

#Get the path of the result file given a TPE folder
def get_results_dir(dir):
	abs_path = os.path.join(get_dir(), dir)
	abs_path = os.path.join(abs_path, 'output')
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, 'competition')
	return abs_path


def read_scores(tpe_dir):
	results_dir = get_results_dir(tpe_dir)
	outfile = os.path.join(results_dir, "submissionScores.csv")
	
	with open(outfile) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if row[0] == 'Submission Score':
				return round(float(row[-1]), 2)

def read_timestamp(tpe_dir):
	results_dir = get_results_dir(tpe_dir)
	outfile = os.path.join(results_dir, "submissionScores.csv")
	timestamp = os.path.getmtime(outfile)
	return timestamp

def check_file_existence(tpe_dir):
	return os.path.exists(os.path.join(get_results_dir(tpe_dir), "rawScores.csv"))


#Loads the dicationnary of {KPI: mean, std} from working directory
def loadStandardization(dict_name = "standardizationParameters.csv"):
	params = {}
	with open(dict_name) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			params[row[0]] = (float(row[1]), float(row[2]))
	return params

#Load weights from working directory
def load_weights():
	dict_name = "scoringWeights.csv"
	dic = {}
	with open(dict_name) as csvfile:
		df = pd.read_csv(csvfile)
		kpi_names = list(df.columns)
		for name in kpi_names:
			dic[name] = list(df[name])[0]
	return dic

#Returns a dict of {KPI: (it0, it1, ..., it20)}			
def retrieve_KPIs(tpe_dir):
	path = os.path.join(get_results_dir(tpe_dir), "rawScores.csv")
	dic = {}

	if not check_file_existence(tpe_dir):
		return

	with open(path) as csvfile:
		df = pd.read_csv(csvfile)
		kpi_names = list(df.columns)
		for name in kpi_names:
			dic[trans_dict[name]] = list(df[name])
	return dic

#Returns a list score stored by iteration number
def computeIntermediateScores(kpis_dict, standards, weights):
	scores = []
	iters = kpis_dict['Iteration']
	for i in iters:
		s = 0
		nb_params = 0
		for k in weights:
			nb_params+=1
			w = weights[k]
			mean, std = standards[k]
			value = kpis_dict[k][i]
			s += w*(value - mean)/std
		scores.append(s/nb_params)

	return [scores[0], scores[5], scores[10], scores[20], scores[-1]]	


if __name__ == "__main__":
	standards = loadStandardization()
	weights = load_weights()
	l = len(sub_list())
	for i in range(10):

		kpis = retrieve_KPIs(sub_list()[random.randint(0, l-1)])

		if kpis==None or len(kpis['Iteration']) < 30:
			continue

		scores = computeIntermediateScores(kpis, standards, weights)
		plt.plot([0, 5, 10, 20, 30], scores)

	plt.xlabel('Iteration number')
	plt.ylabel('Score')
	plt.title('Score evolution for 10 random data points of TPE')
	plt.savefig("iters_evol.png")
	
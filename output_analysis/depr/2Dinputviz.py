
import os
import sys
import csv
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import random
from scipy.interpolate import griddata
import numpy as np

sys.path.extend('./../')

MODE_CHOICES = ['car', 'drive_transit', 'ride_hail', 'walk', 'walk_transit']

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
	return [dir for dir in next(os.walk(current_dir))[1] if dir[0]=='5' and check_file_existence(dir)]

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
	outputs =  os.path.exists(os.path.join(get_results_dir(tpe_dir), "submissionScores.csv"))
	inputs = os.path.exists(os.path.join(getInputsDir(tpe_dir), "MassTransitFares.csv"))
	return inputs and outputs

#Loads the dicationnary of {KPI: mean, std} from working directory
def loadStandardization():
	dict_name = "standardizationParameters.csv"
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

def getTimeSortedDirs():
	dirs = sub_list()
	dirs = sorted(dirs, key = lambda x:read_timestamp(x))
	print("Number of complete result directories : "+str(len(dirs)))
	return dirs

def getInputsDir(tpe_dir):
	abs_path = os.path.join(get_dir(), tpe_dir)
	abs_path = os.path.join(abs_path, 'submission-inputs')
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	return abs_path


def getInputs(tpe_dir):
	path = os.path.join(getInputsDir(tpe_dir), "MassTransitFares.csv")	
	dic = {}
	with open(path) as csvfile:
		df = pd.read_csv(csvfile, index_col=2)
		dic["AdultFare"] = df["amount"][0]
		dic["ChildrenFare"] = df["amount"][1]
		return dic


def getModeSplit(tpe_dir):
	abs_path = os.path.join(tpe_dir, 'output')
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	path = os.path.join(abs_path, "realizedModeChoice.csv")

	dic = {}

	with open(path) as csvfile:
		df = pd.read_csv(csvfile, index_col=0)

		summ = 0
		for col in df.columns:
			summ += list(df[col])[-1]

		for col in df.columns: 
			dic[col] = round(list(df[col])[-1]/summ, 2)

	return dic
	



#Returns a list score stored by iteration number
def computeWeightedScore(kpis_dict, standards, weights):
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
		scores.append(s/sum(weights.values()))

	return scores[-1]	


#Returns a list score stored by iteration number
#Random array contains 10 random folder numbers
def ScoreEvolutionIters(dirs, weights, title = "Score_evol"):

	plt.cla()

	for f in dirs:
		#Load standards and data point KPIS
		standards = loadStandardization()
		kpis_dict = retrieve_KPIs(f)

		#Populate weighted scores from raw scores
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
			scores.append(s/sum(weights.values()))

		#For readability, we do not want to display all points
		X = [0, 5, 10, 20, 29]
		Y = [scores[0], scores[5], scores[10], scores[20], scores[29]]

		plt.plot(X,Y)

	plt.title(title +" KPI evolution for 10 random data points of TPE")
	plt.xlabel("Iteration Number")
	plt.ylabel("Score")
	plt.savefig("ItersEvol/" + title + "__ITERS_EVOL.png")	



def colorMap(dirs, weights, title = "Score"):

	plt.clf()
	standards = loadStandardization()

	x = []
	y = []
	z = []

	#This parses data
	for d in dirs:
		points = getInputs(d)
		kpis = retrieve_KPIs(d)
		points["Score"] = computeWeightedScore(kpis, standards, weights)
		x.append(points["AdultFare"])
		y.append(points["ChildrenFare"])
		z.append(points["Score"])
	
	#This is incomplete data
	x = np.array(x)
	y = np.array(y)
	z = np.array(z)

	#This is complete, interpolated data
	xi = np.linspace(0, 10, 100)
	yi = np.linspace(0, 10, 100)
	data = np.vstack((x,y)).transpose()
	X, Y = np.meshgrid(xi, yi)
	Z = griddata(data, z, (X,Y), method='linear')

	# contour the gridded data, plotting dots at the nonuniform data points.
	plt.contour(X, Y, Z, 10, linewidths=0.5, colors='k')
	plt.contourf(X, Y, Z, 10,  vmax=np.nanmax(Z), vmin=np.nanmin(Z))
	plt.colorbar() 
	plt.scatter(x, y, c='r', marker='o', s=5, zorder=10)


	#Plot parameters
	plt.xlabel("Adult Mass Transit Fare")
	plt.ylabel("Children Mass Transit Fare")
	plt.xlim(0, 10)
	plt.ylim(0, 10)
	plt.title(title)

	#Save figure
	plt.savefig("ColorMaps/" + title + "__COLOR_MAP.png")
	

def colorMapToModeSplit(dirs):

	plt.clf()

	x = []
	y = []
	z = []

	for d in dirs:
		points = getInputs(d)
		x.append(points["AdultFare"])
		y.append(points["ChildrenFare"])

	for mode in MODE_CHOICES:

		print("Creating color map to mode : " + mode)

		plt.clf()

		z = []
		for d in dirs:
			ms = getModeSplit(d)
			z.append(ms[mode])

		#This is complete, interpolated data
		xi = np.linspace(0, 10, 100)
		yi = np.linspace(0, 10, 100)
		data = np.vstack((x,y)).transpose()
		X, Y = np.meshgrid(xi, yi)
		Z = griddata(data, z, (X,Y), method='linear')

		# contour the gridded data, plotting dots at the nonuniform data points.
		plt.contour(X, Y, Z, 10, linewidths=0.5, colors='k')
		plt.contourf(X, Y, Z, 10,  vmax=np.nanmax(Z), vmin=np.nanmin(Z))
		plt.colorbar() 
		plt.scatter(x, y, c='r', marker='o', s=5, zorder=10)


		#Plot parameters
		plt.xlabel("Adult Mass Transit Fare")
		plt.ylabel("Children Mass Transit Fare")
		plt.xlim(0, 10)
		plt.ylim(0, 10)
		plt.title(mode + " mapped to fares")

		#Save figure
		plt.savefig("ColorMaps/" + mode + "__COLOR_MAP.png")

		
			



if __name__ == "__main__":


	os.makedirs("ColorMaps", exist_ok=True)
	os.makedirs("ItersEvol", exist_ok=True)

	weights = load_weights()
	dirs = getTimeSortedDirs()
	

	#Inputs to mode split
	colorMapToModeSplit(dirs)

	k = list(weights.keys())

	#Keep the same data points for all figures
	randomList = [dirs[random.randint(0, len(dirs)-1)] for i in range(10)]

	#Generate iters evol for each KPI
	for i in range(len(k)):
		print("Creating iterations evolution graph for KPI " + k[i])
		#Change keys in dictionnary : generate "vector base" of weigth space
		for j in range(len(k)):
			if i == j:
				weights[k[j]] = 1.0
			else:
				weights[k[j]] = 0.0

		ScoreEvolutionIters(randomList, weights, k[i])

	#Generate aggregate colorMap
	print("Creating aggrgate iterations evolution graph")
	for j in range(len(k)):
		weights[k[j]] = 1.0
	ScoreEvolutionIters(randomList, weights, "Aggregate")

	for i in range(len(k)):
		print("Creating color map for KPI " + k[i])
		#Change keys in dictionnary
		for j in range(len(k)):
			if i == j:
				weights[k[j]] = 1.0
			else:
				weights[k[j]] = 0.0

		colorMap(dirs, weights, k[i])



	#Generate aggregate colorMap
	print("Generating aggregate color map")
	for j in range(len(k)):
		weights[k[j]] = 1.0
	colorMap(dirs, weights, "Aggregate")




	


	
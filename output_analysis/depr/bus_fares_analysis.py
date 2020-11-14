import os
import sys
import csv
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import random
from scipy.interpolate import griddata
import numpy as np

from collect_inputs import *
from collect_outputs import *

from Sample import *

sys.path.extend('./../')

MODE_CHOICES = ['car', 'drive_transit', 'ride_hail', 'walk', 'walk_transit']

#rawScores.csv does not use the same KPI names as the fixed data files...


samples = create_samples_list();
standards = loadStandardization();
weights = load_weights();
	

#Returns a list score stored by iteration number
#Random array contains 10 random folder numbers
def ScoreEvolutionIters(samples, title = "Score_evol"):

	plt.clf()

	for s in samples:
		#Load standards and data point KPIS
		kpis_dict = s.KPIS

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



def colorMap(samples, weights, title = "Score"):

	plt.clf()
	standards = loadStandardization()

	x = []
	y = []
	z = []

	#This parses data
	for s in samples:
		x.append(s.mass_transit_fares["AdultFare"])
		y.append(s.mass_transit_fares["ChildrenFare"])
		z.append(computeWeightedScores(s, standards, weights)[-1])
	
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
	

def colorMapToModeSplit(samples):

	plt.clf()

	x = []
	y = []
	z = []

	for s in samples:
		points = s.mass_transit_fares
		x.append(points["AdultFare"])
		y.append(points["ChildrenFare"])

	for mode in MODE_CHOICES:

		print("Creating color map to mode : " + mode)

		plt.clf()

		z = []
		for s in samples:
			ms = s.mode_split
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
	colorMapToModeSplit(samples)

	k = list(weights.keys())

	#Keep the same data points for all figures
	randomList = [dirs[random.randint(0, len(dirs)-1)] for i in range(10)]
	randomSamples = create_samples_list(randomList)

	#Generate iters evol for each KPI
	for i in range(len(k)):
		print("Creating iterations evolution graph for KPI " + k[i])
		#Change keys in dictionnary : generate "vector base" of weigth space
		for j in range(len(k)):
			if i == j:
				weights[k[j]] = 1.0
			else:
				weights[k[j]] = 0.0

		ScoreEvolutionIters(randomSamples, k[i])

	#Generate aggregate colorMap
	print("Creating aggrgate iterations evolution graph")
	for j in range(len(k)):
		weights[k[j]] = 1.0
	ScoreEvolutionIters(randomSamples, "Aggregate")


	for i in range(len(k)):
		print("Creating color map for KPI " + k[i])
		#Change keys in dictionnary
		for j in range(len(k)):
			if i == j:
				weights[k[j]] = 1.0
			else:
				weights[k[j]] = 0.0

		colorMap(samples, weights, k[i])



	#Generate aggregate colorMap
	print("Generating aggrgate color map")
	for j in range(len(k)):
		weights[k[j]] = 1.0
	colorMap(samples, weights, "Aggregate")





	


	
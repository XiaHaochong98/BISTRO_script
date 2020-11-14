import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os
from math import *
import sys 
import pandas as pd

sys.path.append(os.path.abspath("../fixed_data/"))
from KPIS import *

sys.path.append(os.path.abspath("../utilities/"))
from Sample import *
from collect_inputs import *
from navigate_data import *

MIN_X = 676949
MAX_X = 689624

MIN_Y = 4818750
MAX_Y = 4832294


def getSiouxFauxLinks():
	rows = {}
	avg = 0
	for row in load_network():
		if row[0].isdigit():
			fX,fY,tX,tY = float(row[-4]),float(row[-3]),float(row[-2]),float(row[-1])
			rows[row[0]] = (fX, fY, tX, tY)

	return rows

def getSiouxFauxLinksCongestion(sample): #Congestion being total trips/capacity
	links = {}
	d = sample.directory
	link_stats_path = os.path.join(get_results_dir(d),"link_stats.csv")

	#Open the sample's link stats
	csvfile = open(link_stats_path, "rt")

	reader = csv.reader(csvfile)
	sample_stats = {}
	for r in reader:
		sample_stats[r[0]] = r[1:] 

	#For each link in both the network and the sample, compute congestion
	for row in load_network():
		if row[0].isdigit() and row[0] in sample_stats:
			fX,fY,tX,tY = float(row[-4]),float(row[-3]),float(row[-2]),float(row[-1])
			congestion = 100/24*float(sample_stats[row[0]][1])/float(sample_stats[row[0]][3])*float(sample_stats[row[0]][1])
			links[row[0]] = (congestion,fX,fY,tX,tY)

	return links




def best_scores_link_tolls(samples, standards, KPI, name, folder, percent = 0.1):
	links = getSiouxFauxLinks()
	links = list(links.values())
	weighted_tolls = [0 for i in range(len(links))]

	print("    Generating best " + name + " avg link tolls")

	samples = sorted(samples, key=lambda x:computeWeightedScores(x, standards, KPI)[-1])
	for s in samples[:int(percent*len(samples))]:
		xc,yc,r = s.road_pricing["x"], s.road_pricing["y"], s.road_pricing["r"]
		p = s.road_pricing["p"]

		for i,l in enumerate(links):
			fX,fY,tX,tY = l
			if (fX - xc)**2 + (fY - yc)**2 < r**2 and (tX - xc)**2 + (tY - yc)**2 < r**2:
				weighted_tolls[i] += p/(percent*len(samples))

	fig, ax = plt.subplots()

	tolls_max = max(weighted_tolls)
	tolls_min = min(weighted_tolls)
	lmin, lmax = None, None

	for i in range(len(links)):
		X = [links[i][0], links[i][2]]
		Y = [links[i][1], links[i][3]]
		c = [1 - (weighted_tolls[i] - tolls_min)/(tolls_max-tolls_min), (weighted_tolls[i] - tolls_min)/(tolls_max-tolls_min), 0]
		if weighted_tolls[i]==tolls_min:
			lmin, = ax.plot(X,Y,color=c, label="min")
		if weighted_tolls[i]==tolls_max:
			lmax, = ax.plot(X,Y,color=c, label="max")
		else:
			ax.plot(X,Y,color=c)

	tolls_min = round(tolls_min, 2)
	tolls_max = round(tolls_max, 2)
	if tolls_max - tolls_min < 0.01:
		print("Tolls max == tolls min, abandoning this one")
		return;

	plt.legend((lmin, lmax), (str(tolls_min)+"$/m", str(tolls_max)+"$/m"))

	plt.title("Average toll "+ name +", "+ str(int(100*percent)) + "% best samples")
	
	os.makedirs(folder+"/tolls", exist_ok=True)
	filepath = folder+"/tolls"+"/toll_coloring_"+name+".png"
	plt.savefig(filepath)
	print("    Saved tollmap to: "+filepath)


def best_scores_link_congestion(samples, standards, KPI, name, folder, percent=0.1):
	print("    Generating link congestion coloring for best " + name + " samples")
	samples = sorted(samples, key=lambda x:computeWeightedScores(x, standards, KPI)[-1])
	
	links = {}
	coo = getSiouxFauxLinks()

	for row in load_network():
		if row[0].isdigit():
			links[row[0]]=0

	nb_samples = int(percent*len(samples))

	for s in samples[:nb_samples]:
		sample_congestion = getSiouxFauxLinksCongestion(s)
		for k in sample_congestion.keys():
			links[k] +=sample_congestion[k][0]/nb_samples

	#Right now we have a dictionnary with linkId, congestion and coos
	cong_max = max([links[k] for k in links.keys()])
	cong_min = min([links[k] for k in links.keys()])

	fig, ax = plt.subplots()

	for i in links.keys():
		X = [coo[i][0], coo[i][2]]
		Y = [coo[i][1], coo[i][3]]
		c = [1 - (links[i] - cong_min)/(cong_max-cong_min), (links[i] - cong_min)/(cong_max-cong_min), 0]
		if links[i]==cong_min:
			lmin, = ax.plot(X,Y,color=c, label="min")
		if links[i]==cong_max:
			lmax, = ax.plot(X,Y,color=c, label="max")
		else:
			ax.plot(X,Y,color=c)

	plt.legend((lmin, lmax), (str(round(cong_min,2))+ "% capacity", str(round(cong_max,2))+"% capacity"))

	plt.title("Average congestion "+ name +", "+ str(int(100*percent)) + "% best samples")
	
	os.makedirs(folder+"/congestion", exist_ok=True)
	filepath = folder+"/congestion"+"/congestion_coloring_"+name+".png"
	plt.savefig(filepath)
	print("    Saved congestion map to: "+filepath)

	return;

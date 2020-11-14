from Sample import *
from collect_inputs import *
from KPIS import *
import matplotlib.pyplot as plt
import pandas as pd

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
file = open(os.path.join(dir_path,"unstd_bau.csv"))
df = pd.read_csv(file, index_col = "KPI")

#print(list(df.index))
#print(df['BAU_multiplier']['VMT'])


def swap(list, i, j):
	a = list[i]
	list[i] = list[j]
	list[j] = a


def compute_scores(s, standards, KPI):
	global df
	return df['BAU_multiplier'][KPI] * s.KPIS[KPI][-1]

def sort2(liste, fun, standards, KPI1, KPI2):
	l = len(liste)
	for i in range(l-1):
		for j in range(l-1):
			if inferior(liste[j+1], liste[j], standards, KPI1, KPI2):
				swap(liste, j, j+1)

def pareto_front(samples, standards, KPI1, KPI2):

	points = [] #A point is made of a triplet (s, KPI1, KPI2)
	for s in samples:
		congestion = computeWeightedScores(s, standards, KPI1)[-1]
		social = computeWeightedScores(s, standards, KPI2)[-1]

		#No stds
		#congestion = compute_scores(s, standards, KPI1)
		#social = compute_scores(s, standards, KPI2)
		
		points.append((s, congestion, social))


	non_pareto = []
	pareto = []

	for p in points:
		pa = True
		for q in points:
			if dominates(q[1:], p[1:]):
				pa = False
		if pa:
			pareto.append(p)
		else:
			non_pareto.append(p)

	sort2(pareto, inferior, standards, KPI1, KPI2)
	return (pareto, non_pareto)



def dominates(k1, k2):
	#K1 dominates k2 if k1_i <= k2_i for all i and at least one ineq is strict
	one_strict = False

	for i in range(len(k1)):
		if k1[i] > k2[i]:
			return False
		if k1[i] < k2[i]:
			one_strict = True

	return one_strict

def inferior(par1, par2, standards, KPI1, KPI2):
	x1 = computeWeightedScores(par1[0], standards, KPI1)[-1]
	y1 = computeWeightedScores(par1[0], standards, KPI2)[-1]
	x2 = computeWeightedScores(par2[0], standards, KPI1)[-1]
	y2 = computeWeightedScores(par2[0], standards, KPI2)[-1]

	#x1 = compute_scores(par1[0], standards, KPI1)
	#y1 = compute_scores(par1[0], standards, KPI2)
	#x2 = compute_scores(par2[0], standards, KPI1)
	#y2 = compute_scores(par2[0], standards, KPI2)

	if x1 < x2:
		return True
	if x1 > x2:
		return False
	else:
		if y1 < y2:
			return True
		else:
			return False

def save_samples_pareto(pareto_list, KPI1_name, KPI2_name, folder):
	path = folder+"/pareto_"+KPI1_name+"_"+KPI2_name+".txt"
	file = open(path, "w")
	for s in pareto_list:
		file.write(s[0].directory+"\n")
	file.close()
	print("    Saved pareto list to: "+path)

def plot_pareto(samples, standards, KPI1, KPI2, KPI1_name, KPI2_name, folder):
	
	#KPI1 = list(KPI1.keys())[0]
	#KPI2 = list(KPI2.keys())[0]

	print("    Generating pareto front for "+KPI1_name+ " and "+ KPI2_name)
	pareto, non_pareto = pareto_front(samples, standards, KPI1, KPI2)

	plt.clf()

	for p in pareto:
		plt.plot(p[1], p[2], 'ro')

	for p in non_pareto:
		plt.plot(p[1], p[2], 'xb')



	for i in range(len(pareto) - 1):
		plt.plot([pareto[i][1], pareto[i+1][1]], [pareto[i][2], pareto[i+1][2]],color="black")

	x_min = min(p[1] for p in pareto + non_pareto)
	x_max = max(p[1] for p in pareto + non_pareto)
	y_min = min(p[2] for p in pareto + non_pareto)
	y_max = max(p[2] for p in pareto + non_pareto)

	plt.plot([x_min, x_min], [pareto[0][2], 1000000], color='black')
	plt.plot([pareto[len(pareto) - 1][1], 100000], [y_min, y_min], color='black')

	plt.xlim((x_min - 0.4, x_max + 0.4))
	plt.ylim((y_min - 0.4, y_max + 0.4))
	plt.xlabel(KPI1_name)
	plt.ylabel(KPI2_name)
	plt.title("Pareto front " + KPI1_name + " " + KPI2_name)

	filepath = folder+"/pareto_"+KPI1_name+"_"+KPI2_name+".png"
	plt.savefig(filepath)
	print("    Saved pareto front to: "+filepath)

	plt.savefig("pareto.png")

	save_samples_pareto(pareto, KPI1_name, KPI2_name, folder)

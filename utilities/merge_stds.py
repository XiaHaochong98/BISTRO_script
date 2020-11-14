#########################################
#										#
#	Merges two CSV standardizarions     #
#										#
#########################################

import pandas as pd

#Arguments:

#Path of first standardization file
path1 = "../fixed_data/per_mile_stds.csv"

#Number of standardizing samples
n1 = 627

#Path of second standardization file
path2 = "../fixed_data/cordon_stds.csv"

#Number of standardizing samples
n2 = 488


stds1 = pd.read_csv(open(path1), index_col = 0, names = ["KPI","mean","std"])
stds2 = pd.read_csv(open(path2), index_col = 0, names = ["KPI","mean","std"])

stds3 = open("merged_stds.csv", "w")
KPIS = list(stds1['mean'].keys())

for k in KPIS:
	mean1 = stds1['mean'][k]
	std1 = stds1['std'][k]

	mean2 = stds2['mean'][k]
	std2 = stds2['std'][k]

	mean_m = (n1*mean1 + n2*mean2)/(n1 + n2)
	var_m = n1*(std1**2 + (mean1 - mean_m)**2) + n2*(std2**2 + (mean2 - mean_m)**2)
	var_m = (var_m/(n1 + n2))**0.5

	stds3.write(k+','+str(mean_m)+','+str(var_m)+'\n')
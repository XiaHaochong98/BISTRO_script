from Sample import *
from collect_inputs import *
from collect_outputs import *
from Sample import *
from KPIS import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import sys

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
file = open(os.path.join(dir_path,"unstd_bau.csv"))
df = pd.read_csv(file, index_col = "KPI")

#Alpha used in laffer curves
a = 0.15

# THINGS I CHANGED
# collect_outputs.py: VEHICLES variable, getModeSplit line
# graphing.py: added laffer, commented out other graphs
# laffer.py: created file

def colors_iter():
    colors = ['y','k','g','c']
    i = 0
    while True:
        yield colors[i%len(colors)]
        i += 1

def compute_laffer(samples, standards):
	global sample_index
	sample_index = 0

	toll_revenues = []
	car_ridehail_VMTs = []
	equivalent_tax_rates = []
	road_prices = []
	tolled_VMTs = []
	tolled_VMTs_per_trip = []
	VMT_ratio = []
	toll_eligible_trips = []
	# maybe change to be ndarray zeros
	# then update by index in loop, leave as 0 if sample error

	for s in samples:
		#print(sample_index)
		price = s.road_pricing["p"]
		#print("ROAD PRICE: " + str(price))
		trips = s.mode_split.get("ride_hail", 0) + s.mode_split.get("car", 0)

		if len(s.KPIS["TollRevenue"]) == 0:
			tr = 0.0
		else:
			tr = s.KPIS["TollRevenue"][-1]
		#print("TOTAL REVENUE: " + str(tr))
		
		if len(s.KPIS["VMT"]) == 0:
			car_ridehail_vmt = 0.0
		else:
			car_ridehail_vmt = s.KPIS["VMT"][-1]
		#print("CAR-RIDEHAIL VMT: " + str(car_ridehail_vmt))

		if car_ridehail_vmt == 0:
			equivalent_tax_rate = 0.0
		else:
			equivalent_tax_rate = tr / car_ridehail_vmt

		# tolled vmt = vmt within cordon
		if tr == 0:
			tolled_VMT = 0.0
		else:
			tolled_VMT = tr / price
		
		# avg_tolled_VMT_per_trip = tolled_VMT / trips
		# ratio = tolled_VMT / car_ridehail_vmt

		#print("EQUIV TAX RATE: " + str(equivalent_tax_rate))
		#print("TOLLED VMT: " + str(tolled_VMT))

		toll_revenues.append(tr)
		equivalent_tax_rates.append(equivalent_tax_rate)
		road_prices.append(price)
		car_ridehail_VMTs.append(car_ridehail_vmt)
		tolled_VMTs.append(tolled_VMT)
		toll_eligible_trips.append(trips)
		# tolled_VMTs_per_trip.append(avg_tolled_VMT_per_trip)
		# VMT_ratio.append(ratio)
		sample_index += 1

	sample_indices = list(range(sample_index))

	data = list(zip(toll_revenues, equivalent_tax_rates, road_prices, car_ridehail_VMTs, toll_eligible_trips))
	colnames = ["toll_revenue","equivalent_tax_rate","road_price","car_ridehail_VMT", "toll_eligible_trips"]
	df = pd.DataFrame(data, index=sample_indices, columns=colnames)
	return df



def save_laffer_csv(df, folder):
	# data should be list of lists
	# each of length num_samples
	path = folder+"/laffer_data.csv"
	file = open(path, "w")
	# write column names
	# file.write("sample_index,toll_revenue,equivalent_tax_rate,road_price,car_ridehail_VMT,VMT_ratio,tolled_VMT_per_trip\n")
	# for s in zip(data):
	# 	# write data
	# 	for item in s:
	# 		file.write(item+",")
	# 	file.write("\n")
	df.to_csv(path)
	print("    Saved laffer data to: "+path)


def get_best_agg_samples(samples, standards, folder, KPIS, KPIS_names):

	dic = {}
	for k,n in zip(KPIS, KPIS_names):
		if n[:3] == "Agg":
			num = n[3]
			best_sample = sorted(samples, key = lambda s:computeWeightedScores(s, standards, k)[-1])[0]
			
			if best_sample not in dic:
				dic[best_sample] = [num]
			else:
				dic[best_sample].append(num)
				dic[best_sample] = sorted(dic[best_sample])

	return dic

def plot_laffer_std(samples1, standards, folder, KPIS, KPIS_names, samples2 = None):
	
	os.makedirs(folder+"/laffer_std", exist_ok = True)

	samples = samples1
	if samples2 is not None:
		samples += samples2

	dic = get_best_agg_samples(samples, standards, folder, KPIS, KPIS_names)

	#To be used with something that's not road pricing
	samples_etr = {}
	for s in samples:
		price = s.road_pricing["p"]
		tr = s.KPIS["TollRevenue"][-1]
		vmt = s.KPIS["VMT"][-1]
		trips =  s.mode_split.get("ride_hail", 0) + s.mode_split.get("car", 0)
		tolled_VMT = tr/price
		tolled_VMT_per_trip = tolled_VMT/trips

		etr = price*tolled_VMT_per_trip
		samples_etr[s] = etr


	for kpi,kn in zip(KPIS, KPIS_names):
		plt.clf()
		RP = []
		KP = []

		for s in samples1:
			rp = s.road_pricing["p"]
			KP.append(computeWeightedScores(s, standards, kpi)[-1])
			RP.append(samples_etr[s])
		plt.plot(RP, KP, "xb", alpha = a)

		RP = []
		KP = []
		for s in samples2:
			rp = s.road_pricing["p"]
			KP.append(computeWeightedScores(s, standards, kpi)[-1])
			RP.append(samples_etr[s])
		plt.plot(RP, KP, "xr", alpha = a)

		#Add red points for best samples --> Change this to compute weighted score
		legend = []
		gen = colors_iter()
		for k in dic:
			v = dic[k]
			plt.plot(samples_etr[k], computeWeightedScores(k, standards, kpi)[-1], 'o' + next(gen))
			l = "Best for agg "
			for n in v:
				l += str(n) + " "
			legend.append(l)

		plt.legend(["Laffer points RS", "Laffer points OPTIM"] + legend)
		plt.title(kn + " as a function road pricing")
		plt.xlabel("road price x average tolled VMT per trip ($)")
		plt.ylabel(kn)

		plt.savefig(folder+"/laffer_std/laffer_std_"+kn+".png", bbox_inches='tight')
		print("    Saved " + kn + " road pricing curve plot to: "+folder+"/laffer_std/laffer_std_"+kn+".png")




def plot_laffer_unstd(samples1, standards, folder, KPIS, KPIS_names, samples2 = None):
	
	os.makedirs(folder+"/laffer_raw", exist_ok = True)

	samples = samples1
	if samples2 is not None:
		samples += samples2

	dic = get_best_agg_samples(samples, standards, folder, KPIS, KPIS_names)

	samples_etr = {}
	for s in samples:
		price = s.road_pricing["p"]
		tr = s.KPIS["TollRevenue"][-1]
		vmt = s.KPIS["VMT"][-1]
		trips =  s.mode_split.get("ride_hail", 0) + s.mode_split.get("car", 0)
		tolled_VMT = tr/price
		tolled_VMT_per_trip = tolled_VMT/trips

		etr = price*tolled_VMT_per_trip
		samples_etr[s] = etr


	#Toll Revenue
	plt.clf()
	RP = []
	TR = []

	for s in samples1:
		rp = s.road_pricing["p"]
		TR.append(s.KPIS["TollRevenue"][-1])
		RP.append(samples_etr[s])
	plt.plot(RP, TR, "xb", alpha = a)

	RP = []
	TR = []

	for s in samples2:
		rp = s.road_pricing["p"]
		TR.append(s.KPIS["TollRevenue"][-1])
		RP.append(samples_etr[s])
	plt.plot(RP, TR, "xr", alpha = a)

	#Add red points for best samples
	gen = colors_iter()
	legend = []
	for k in dic:
		v = dic[k]
		plt.plot(samples_etr[k], k.KPIS["TollRevenue"][-1], 'o' + next(gen))
		l = "Best for agg "
		for n in v:
			l += str(n) + " "
		legend.append(l)

	plt.legend(["Laffer points RS", "Laffer points OPITM"] + legend)
	plt.title("Laffer curve")
	plt.xlabel("road price x average tolled VMT per trip ($)")
	plt.ylabel("Toll Revenue")

	plt.savefig(folder+"/laffer_raw/laffer_TR.png", bbox_inches='tight')
	print("    Saved laffer curve plot to: "+folder+"/laffer_raw/laffer_TR.png")


	#VMT
	plt.clf()
	RP = []
	VMT = []

	for s in samples1:
		VMT.append(s.KPIS["VMT"][-1])
		RP.append(samples_etr[s])
	plt.plot(RP, VMT, "xb", alpha = a)

	RP = []
	VMT = []

	for s in samples2:
		VMT.append(s.KPIS["VMT"][-1])
		RP.append(samples_etr[s])
	plt.plot(RP, VMT, "xr", alpha = a)

	#Add red points for best samples
	gen = colors_iter()
	legend = []
	for k in dic:
		v = dic[k]
		plt.plot(samples_etr[k], k.KPIS["VMT"][-1], 'o' + next(gen))
		l = "Best for agg "
		for n in v:
			l += str(n) + " "
		legend.append(l)
	plt.legend(["Laffer points RS", "Laffer points OPTIM"] + legend)
	plt.title("Vehicle miles traveled vs Average trip cost")
	plt.xlabel("road price x average tolled VMT per trip ($)")
	plt.ylabel("VMT")

	plt.savefig(folder+"/laffer_raw/laffer_VMT.png", bbox_inches='tight')
	print("    Saved laffer curve plot to: "+folder+"/laffer_raw/laffer_VMT.png")


	#Raw data
	raw_kpis = list(samples[0].raw_data.keys())
	for kpi in raw_kpis:

		plt.clf()
		RP = []
		KP = []

		for s in samples1:
			KP.append(s.raw_data[kpi])
			RP.append(samples_etr[s])
		plt.plot(RP, KP, "xb", alpha = a)

		RP = []
		KP = []
		for s in samples2:
			KP.append(s.raw_data[kpi])
			RP.append(samples_etr[s])
		plt.plot(RP, KP, "xr", alpha = a)
		#Add red points for best samples
		legend = []
		gen = colors_iter()
		for k in dic:
			v = dic[k]
			plt.plot(samples_etr[k], k.raw_data[kpi], 'o'+ next(gen))
			l = "Best for agg "
			for n in v:
				l += str(n) + " "
			legend.append(l)
		plt.legend(["Laffer points RS", "Laffer points OPTIM"] + legend)
		plt.title(kpi + " vs Average trip cost")
		plt.xlabel("road price x average tolled VMT per trip ($)")
		plt.ylabel(kpi)

		plt.savefig(folder+"/laffer_raw/laffer_"+kpi+".png",bbox_inches='tight')
		print("    Saved laffer curve plot to: "+folder+"/laffer_raw/laffer_"+kpi+".png")
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from Sample import *
import matplotlib as mp
import pickle
import os
from matplotlib._png import read_png
from matplotlib.cbook import get_sample_data
from collect_inputs import *
import matplotlib.lines as mlines
from KPIS import *
from math import *


MIN_X = 676949
MAX_X = 689624

MIN_Y = 4818750
MAX_Y = 4832294

NB_GRAPHS = 6 #Used for 5D plots

##CREATE COLOR MAPS
def customColorMap(r, g, b, a):
	colors = [(r, g, b, a), [r, g ,b, a]]  # R -> R
	n_bin = 10  # Discretizes the interpolation into bins
	cmap_name = 'my_list'
	cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bin)
	return cm

return (x ** 2 + y ** 2 - z ** 2)

def scatterRoadPricing(): #5d road pricing

	os.makedirs("4DPlots",exist_ok=True)

	samples = create_samples_list()
	#weights = load_weights()
	standards = loadStandardization()

	title = " = f(x,y,r,p) "

	xi = []
	yi = []
	ri = []
	pi = []
	si = []

	for s in samples:
		xi.append(s.road_pricing["x"])
		yi.append(s.road_pricing["y"])
		ri.append(s.road_pricing["r"])
		pi.append(s.road_pricing["p"])


	KPIS = [congestion_KPI, social_KPI, aggregate_KPI]
	KPIS_names = ["congestion","social", "aggregate" ]
	for i in range(len(KPIS)):
		name = KPIS_names[i]
		k = KPIS[i]

		print("Creating figures for KPI : " + name)

		si = []
		for s in samples:
			si.append(computeWeightedScores(s, standards, k)[-1])


		scatterBinnedPoints(xi, yi, ri, pi, si, name + title, name + "/")


def scatterBinnedPoints(xi, yi, zi, ti, vi, title, folder):

	os.makedirs("4DPlots/" + folder, exist_ok=True)

	bins = [min(ti) + i/NB_GRAPHS*(max(ti) - min(ti)) for i in range(NB_GRAPHS)] + [max(ti)]
	for i in range(NB_GRAPHS):
		inf = bins[i]
		sup = bins[i+1]
		b_string = "[p = " + str(round(inf, 1)) + " ; " + str(round(sup, 1)) + "p = "


		x,y,z,v = [],[],[],[]
		for j in range(len(xi)):
			if ti[j] >= inf and ti[j] <= sup:
				x.append(xi[j])
				y.append(yi[j])
				z.append(zi[j])
				v.append(vi[j])

		print("    Scattering points for bin " + str(i) + "/" + str(NB_GRAPHS))
		scatterAllPoints(x, y, z, v, title + b_string, folder)


def scatterAllPoints(xi, yi, zi, vi, title, folder=""):

	plt.clf()

	fig = plt.figure()
	ax = plt.axes(projection='3d')
	ax.set_title(title)
	ax.set_xlabel('x')
	ax.invert_xaxis() #Otherwise 3D projection does not have x and y intersect at their minimum
	ax.set_ylabel('y')
	ax.set_zlabel('r')

	maxi = np.max(vi)
	mini = np.min(vi)
	
	cmap = mp.cm.get_cmap('viridis')
	normalize = mp.colors.Normalize(vmin=min(vi), vmax=max(vi))
	colors = [cmap(normalize(value)) for value in vi]

	ax.scatter(xi, yi, zi, color=colors)

	cax, _ = mp.colorbar.make_axes(ax)
	cbar = mp.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)

	plt.savefig("4DPlots/" + folder + title + ".png")



def scatterByBins():
	#For each X, Y and Z, gets a V value
	points_per_axis = 40

	xs = np.linspace(-6, 6, points_per_axis)
	ys = np.linspace(-6, 6, points_per_axis)
	zs = np.linspace(-6, 6, points_per_axis)
	X,Y,Z = np.meshgrid(xs,ys,zs)
	V = f(X,Y,Z) #30*30*30 array

	#We want to discretize V into several plots of different colors based
	#on the value of V
	nb_bins = points_per_axis
	mini = np.min(V)

	maxi = np.max(V)
	bins = np.linspace(mini, maxi, nb_bins + 1)


	ax.set_xlabel('x')
	ax.set_ylabel('y')
	ax.set_zlabel('z')
	ax.set_xlim3d(-6, 6)
	ax.set_ylim3d(-6, 6)
	ax.set_zlim3d(-6, 6)

	for i in range(nb_bins):
		print("Bin : ",str(i + 1))
		plt.cla()

		ax.set_title('Bin [' + str(round(bins[i], 1)) + " ; " + str(round(bins[i+1], 1)) + "]")
		ax.set_xlabel('x')
		ax.set_ylabel('y')
		ax.set_zlabel('z')
		ax.set_xlim3d(-6, 6)
		ax.set_ylim3d(-6, 6)
		ax.set_zlim3d(-6, 6)

		xi = np.array([])
		yi = np.array([])
		zi = np.array([])
		

		for x in range(points_per_axis):
			for y in range(points_per_axis):
				for z in range(points_per_axis):
					
					if V[x,y,z] > bins[i] and V[x,y,z] <= bins[i+1]:

						xi = np.append(xi,xs[x])
						yi = np.append(yi,ys[y])
						zi = np.append(zi,zs[z])
		
		if len(zi) == 0:
			continue
		ax.scatter(xi, yi, zi, c=[(i/nb_bins,0,1-i/nb_bins,0.3)], vmin=np.nanmin(zi), vmax=np.nanmax(zi))
		plt.savefig("fig"+str(i)+".png")



def plotBestTrafficCircles():
	samples = create_samples_list()
	#weights = load_weights()
	standards = loadStandardization()

	xi = []
	yi = []
	ri = []
	pi = []
	si = []

	for s in samples:

		xi.append(s.road_pricing["x"])
		yi.append(s.road_pricing["y"])
		ri.append(s.road_pricing["r"])
		pi.append(s.road_pricing["p"])

	outputs_ranks = [i for i in range(len(xi))]

	KPIS = [congestion_KPI, social_KPI, aggregate_KPI]
	KPIS_names = ["congestion","social", "aggregate" ]

	for i in range(len(KPIS)):
		name = KPIS_names[i]
		k = KPIS[i]

		print("Creating figures for KPI : " + name)

		si = []
		for s in samples:
			si.append(computeWeightedScores(s, standards, k)[-1])

		outputs_ranks = sorted(outputs_ranks, key=lambda x:si[x])

		plt.clf()

		fig, ax = plt.subplots()

		ax.set_title(name)
		ax.set_xlabel('x')
		ax.set_ylabel('y')
		ax.set_xlim((MIN_X, MAX_X))
		ax.set_ylim((MIN_Y, MAX_Y))

		ax.set_facecolor((0, 0, 0))

		plotSiouxFauxMap(ax)

		for k in range(NB_GRAPHS):
			j = NB_GRAPHS - k - 1
			plotColoredCircle(ax, xi[outputs_ranks[j]], yi[outputs_ranks[j]], ri[outputs_ranks[j]], [0, 0.8, 0, 0.5*j/(NB_GRAPHS - 1)])
			ax.text(xi[outputs_ranks[j]], yi[outputs_ranks[j]], str(round(pi[outputs_ranks[j]], 2)))

		fig.savefig(name+".png")



def cordon_normal_distribution(x,y, xc, yc, sigma, radius):
	r = np.sqrt((x - xc)**2 + (y - yc)**2)
	return np.exp(-(r-radius)**2/(2*sigma**2))
	return 1/np.sqrt(2*pi*sigma**2)*np.exp(-(r-radius)**2/(2*sigma**2))


def cordon_combined_normal_distribution(x,y, factors):
	global sigmas, xcs, ycs, radius
	value = 0
	for i in range(len(xcs)):
		value += factors[i]/len(factors)*cordon_normal_distribution(x,y,xcs[i], ycs[i], sigmas[i], radius[i])
	return value

def score_normalization(x ,mu, sigma):
	return 1/np.sqrt(2*pi*sigma**2)*np.exp(-(x-mu)**2/(2*sigma**2))



def plotTrafficCordonsHeatMap():
	samples = create_samples_list()
	standards = loadStandardization()
	global sigmas, xcs, ycs, radius
	sigmas = []
	xcs = []
	ycs = []
	radius = []

	X, Y = np.meshgrid(np.linspace(MIN_X, MAX_X, 1000), np.linspace(MIN_Y, MAX_Y, 1000))

	#KPIS = [aggregate_KPI, congestion_KPI, social_KPI, TollRevenue_KPI]
	#KPIS_names = ["aggregate", "congestion", "social", "toll_revenue"]
	KPIS = ALL_KPIS
	KPIS_NAMES = ALL_NAMES


	for s in samples:
		if s.road_pricing["r"]!=0: # and s.KPIS["TollRevenue"][-1] !=0:
			xcs.append(s.road_pricing["x"])
			ycs.append(s.road_pricing["y"])
			sigmas.append(s.road_pricing["r"]/4)
			radius.append(s.road_pricing["r"])

	for i in range(len(KPIS)):
		name = KPIS_NAMES[i]
		k = KPIS[i]

		print("Creating figures for KPI : " + name)


		si = []
		for s in samples:
			if s.road_pricing["r"]!=0: # and s.KPIS["TollRevenue"][-1] !=0:
				si.append(computeWeightedScores(s, standards, k)[-1])

		Z = cordon_combined_normal_distribution(X, Y, si)

		fig, ax = plt.subplots()
		z_min, z_max = Z.min(), Z.max()

		Z = (Z - z_min)/z_max
		Z = 1 - Z
		#Z = score_normalization(Z, 0.5, 0.2)


		plotSiouxFauxMap(ax)
		c = ax.pcolormesh(X, Y, Z, cmap='RdBu', vmin=0, vmax=1)
		ax.set_title(name)
		# set the limits of the plot to the limits of the data
		ax.axis([X.min(), X.max(), Y.min(), Y.max()])
		fig.colorbar(c, ax=ax)

		plt.savefig(name+".png")


def plotColoredCircle(ax, x, y, r, color): #color takes and rgba argument as a list	
	circle = plt.Circle((x, y), r, color=color, fill=True)
	circle2 = plt.Circle((x, y), r, color=[1, 0, 0, 1], fill=False)
	ax.add_artist(circle)
	ax.add_artist(circle2)





def plotCityMap():
	plt.clf()
	plt.rcParams['axes.facecolor'] = 'black'
	i = 0
	for row in load_network():
		if row[0].isdigit():
			i+=1
			fromLocationX,fromLocationY,toLocationX,toLocationY = float(row[-4]),float(row[-3]),float(row[-2]),float(row[-1])
			X = [fromLocationX,toLocationX]
			Y = [fromLocationY, toLocationY]
			plt.plot(X, Y, 'w')

			if i%1000==0:
				print("Link ", i)
	plt.savefig("map.png")



def placement_evol():
	samples = create_samples_list()
	standards = loadStandardization()

	KPI = aggregate_KPI
	name = "Aggregate"

	plt.clf()

	for i in range(len(samples)):
		s = samples[i]
		x = s.road_pricing["x"]
		y = s.road_pricing["y"]
		c = [1-i/len(samples), i/len(samples), 0]
		plt.plot(x,y,"o", color=c)

	plt.savefig("pos_evol.png")
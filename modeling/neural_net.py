import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random as random
from Sample import *
from KPIS import *
from collect_inputs import *

MIN_X = 676949
MAX_X = 689624

MIN_Y = 4818750
MAX_Y = 4832294


	
samples = create_samples_list()
standards = loadStandardization()
random.shuffle(samples)

class Net(nn.Module):

    def __init__(self, nbInputs, nbOutputs):

    	super(Net, self).__init__()
    	self.fc1 = nn.Linear(nbInputs, 10)
    	self.fc2 = nn.Linear(10, 10)
    	self.fc3 = nn.Linear(10, nbOutputs)

    	self.criterion = nn.MSELoss()
    	self.optimizer = optim.SGD(self.parameters(), lr=0.003, momentum=0.9)

    def forward(self, x):
    	x = F.relu(self.fc1(x))
    	x = F.relu(self.fc2(x))
    	x = self.fc3(x)
    	return x




#data_points contain (x,y) samples
#No need for mini_batches since there is so little data
def train(net, epochs, x, y, test_x, test_y):
	
	for e in range(100):
		for i in range(epochs//100):

			net.zero_grad()
			output = net(x)
			loss = net.criterion(output,y)

			loss.backward()
			net.optimizer.step()

			#Test progress
			score = test(net, test_x, test_y)
		print("Epoch " + str(e*epochs//100) + " : MSE loss = " + str(score))



def test(net, x, y):
	return net.criterion(net(x), y).item()



#INPUTS : (circle x, circle y, radius, price)
#OUTPUTS : (congestion, social)
def kpi_circle_exp_estimator():


	xi = []
	yi = []

	for s in samples:
		x = (s.road_pricing['x'] - MIN_X)/(MAX_X - MIN_X)
		y = (s.road_pricing['y'] - MIN_Y)/(MAX_Y - MIN_Y)
		r = s.road_pricing['r']/(MAX_Y - MIN_Y)
		p = s.road_pricing['p']/10

		xi.append(np.array([x, y, r, p]))
	
		social = computeWeightedScores(s, standards, social_KPI)[-1]
		congestion = computeWeightedScores(s, standards, congestion_KPI)[-1]

		yi.append(np.array([social, congestion]))



	#Define x, xtest, y, ytest in pytoch friendly format
	TEST_PROPORTION = 0.3
	cutoff = int(len(xi) * (1 - TEST_PROPORTION))

	x = torch.from_numpy(np.array(xi[:cutoff], dtype=np.float32))
	y = torch.from_numpy(np.array(yi[:cutoff], dtype=np.float32))

	x_test = torch.from_numpy(np.array(xi[cutoff:], dtype=np.float32))
	y_test = torch.from_numpy(np.array(yi[cutoff:], dtype=np.float32))

	net = Net(4, 2)

	train(net, 100, x, y, x_test, y_test)

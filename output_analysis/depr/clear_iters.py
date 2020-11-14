
import os
import sys
import csv
import matplotlib.pyplot as plt
import shutil

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
	return os.path.exists(os.path.join(get_results_dir(tpe_dir), "submissionScores.csv"))

def rm_iters_of_run(tpe_dir):
	print("Entering " + tpe_dir)
	abs_path = os.path.join(get_dir(), tpe_dir)
	abs_path = os.path.join(abs_path, 'output')
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, only_subdir(abs_path))
	abs_path = os.path.join(abs_path, 'ITERS')
	paths = []
	if os.path.exists(abs_path):
		paths = paths + [os.path.join(abs_path, dir) for dir in next(os.walk(abs_path))[1] if dir!='it.20']
	for p in paths:
		shutil.rmtree(p)
		print("    Deleted " + p)


def remove():
	runs = sub_list()
	for r in runs:
		rm_iters_of_run(r)


if __name__ == "__main__":
	runs = sub_list()
	for r in runs:
		rm_iters_of_run(r)

	
	
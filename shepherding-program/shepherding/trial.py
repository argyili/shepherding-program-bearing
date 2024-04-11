from .model import sheep
from .model import shepherd_degree
from . import util
from .util import plot_ss as plt
from .method import select_shepherd_method

import csv
import numpy as np
import math
import time

class Trial:
    def __init__(self, param, directory_path):
        self.param = param
        self.shepherd_method = param["shepherd_method"]
        self.trials = param["trial_number"]
        self.n_iter = param["n_iter"]
        self.goal = param["goal"]
        self.radius =  param["goal_radius"]
        self.directory_path = directory_path
        self.file_path_tri_csv = directory_path + "/data/{}.csv" # save each trial. the shepherd number.
        self.file_path_ite_csv = directory_path + "/data/{}sh{}tr{}.csv" # save each iteration. shepherd number / sheep number / trail number.
        self.file_path_ite_csv_v = directory_path + "/data/{}sh{}tr{}_v.csv" # save each iteration. shepherd number / sheep number / trail number.

        if "shepherd_model" not in param:
            self.shepherd_model = 'normal'
        else:
            self.shepherd_model = param["shepherd_model"]

    ''' Update positions in each step '''
    def update(self, sheeps, shepherds, method, step):
        method.update(sheeps, shepherds, step) # Shepherds first update its information
        [shepherds[i].update(sheeps, shepherds, step) for i in range(len(shepherds))] # Shepherds update position
        [sheeps[i].update(sheeps, shepherds) for i in range(len(sheeps))] # Then sheep update position

    ''' Judge whether process over for all shepherd agents '''
    def is_success(self, shepherds):
        success = True
        for i in range(len(shepherds)):
            if not shepherds[i].is_success:
                success = False
                break
        return success
    
    ''' Calculate average shepherding movement in each step '''
    def calculate_step_distance(self, shepherds):
        total_distance = 0
        for i in range(len(shepherds)):
            total_distance += shepherds[i].step_distance
        average_distance = total_distance / len(shepherds)
        return average_distance

    ''' Run a trial with saving a csv '''
    def trial_loop_csv(self, shepherd_num, sheep_num, trial):
        # Initialize all sheep agents
        sheeps = [sheep.Sheep(self.param, i, trial) for i in range(0, sheep_num)]
        [sheeps[i].reset(self.param, i, trial) for i in range(len(sheeps))]

        # Initialize all shepherd agents by shepherd model
        if self.shepherd_model == 'degree':
            shepherds = [shepherd_degree.Shepherd(self.param, i, trial) for i in range(0, shepherd_num)]
        [shepherds[i].reset(self.param, i, trial) for i in range(len(shepherds))]
        
        # Initialize shepherding method
        method = select_shepherd_method(self.shepherd_method, self.param)

        # Write csv file when iterating
        f = open(self.file_path_ite_csv.format(shepherd_num, sheep_num, trial), mode='a')
        writer = csv.writer(f)

        # Flag
        # Success judges shepherdng success or not
        # Distance is the average shepherding distance
        success = False
        distance = 0
        step = self.n_iter
        for i in range(0, self.n_iter+1):
            plt.write_line_csv(writer, sheeps, shepherds) # First write
            self.update(sheeps, shepherds, method, i) # Then update
            distance += self.calculate_step_distance(shepherds)
            if self.is_success(shepherds) == True:
                success = True
                step = i
                break
    
        # Write result in the last line
        # From left to right: shepherd number, sheep number, shepherding method, success or not, step number, average movement ditance 
        result = [shepherd_num, sheep_num, self.shepherd_method, success, step, math.ceil(distance)]
        plt.write_last_line_csv(writer, result)
        f.close()

        return result
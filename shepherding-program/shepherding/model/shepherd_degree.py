import math
import random
import numpy as np
import random
from .module import *

''' 
Proposed shepherding model
'''
class Shepherd:
    def __init__(self,param,i,trial):
        # Common reset
        self.reset(param,i,trial)
        # Specific reset
        self.angle = 0
        self.true_goal = param['goal'] # self.goal may change, but self.true_goal is set not changed        
        self.p1 = param["shepherd_param"][0]
        self.p2 = param['shepherd_param'][1]
        self.p3 = param['shepherd_param'][2]
        if 'shepherd_degree_precision' in param:
            self.precision = param['shepherd_degree_precision']
        else:
            self.precision = 0
        self.thres_orient = param['shepherd_degree'][0] / 180 * math.pi # orientation radian
        self.thres_rotate_1 = param['shepherd_degree'][1] / 180 * math.pi #  switching radian in stage 1
        self.thres_switch_2 = param['shepherd_degree'][2] / 180 * math.pi #  switching radian in stage 2
        self.thres_rotate_2 = param['shepherd_degree'][3] / 180 * math.pi #  switching radian in stage 2
        self.thres_multi_1 = param['shepherd_multi'][0] / 180 * math.pi #  multi-agent radian
        self.thres_multi_2 = param['shepherd_multi'][1] / 180 * math.pi #  multi-agent radian
        self.thres_flock_interval = param['shepherd_flock_interval'] / 180 * math.pi # multi-agent radian
        self.thres_occlusion = param['shepherd_occlusion_angle'] / 180 * math.pi # multi-agent radian
        self.velocity = np.array([0,0])
        self.main_velocity = np.array([0,0])
        self.v1 = np.array([0,0])
        self.v2 = np.array([0,0])
        self.v3 = np.array([0,0])
        self.velocity_list = [np.array([0,0]), np.array([0,0]), np.array([0,0])] # 3 sub-velocities
        self.const_velocity = param['const_velocity']
        self.limit = 3 # Calculation set as 3 in the cube calculation
        self.flag = 0
        self.flag_shepherd_left = False
        self.flag_shepherd_right = False
        
    def reset(self, param, i, trial):
        self = reset_shepherd(self,param,i,trial)

    def update_state(self):
        self.position = self.position + self.velocity
        self.step_distance = np.linalg.norm(self.velocity)
                
        self.v1 = self.p1 * self.v1
        self.v2 = self.p2 * self.v2
        self.v3 = self.p3 * self.v3
        self.v = self.v1 + self.v2 + self.v3

        if np.linalg.norm(self.v) != 0:
            self.velocity = (self.v) / np.linalg.norm(self.v) * self.const_velocity
            self.main_velocity = self.v1 / np.linalg.norm(self.v) * self.const_velocity
            self.velocity_list = [self.v1 / np.linalg.norm(self.v) * self.const_velocity, self.v2 / np.linalg.norm(self.v) * self.const_velocity, self.v3 / np.linalg.norm(self.v) * self.const_velocity]
        else:
            self.velocity = np.array([0,0])
            self.main_velocity = np.array([0,0])
            self.velocity_list = [np.array([0,0]), np.array([0,0]), np.array([0,0])]
        
    ''' 
    Update one shepherd
    Main function
    '''
    def update(self, sheeps, shepherds,step):
        # First move, then calculate velocity for the next time step
        if len(sheeps) == 0: return

        self.sheeps = sheeps
        self.shepherds = shepherds
        
        self.judge_success()
        if self.is_success: return

        self.update_state() 
    
    ''' 
    Judge globally whether the shepherding is completed
    '''
    def judge_success(self):
        success = True
        for i in range(len(self.sheeps)):
            u = self.sheeps[i].position - self.goal
            d = np.linalg.norm(u)
            if d > self.goal_radius:
                success = False
                break
        self.is_success = success
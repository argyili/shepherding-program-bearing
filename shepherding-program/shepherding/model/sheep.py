import math
import random
import numpy as np
import time 

class Sheep:
    def __init__(self, param, i, trial):
        # Initialize
        self.R = param["sheep_range"]
        self.no = i
        self.p1_c = param["sheep_param"][0] # cohesion
        self.p1_s = param["sheep_param"][1] # separation
        self.p2 = param["sheep_param"][2] # alignment
        self.p3 = param["sheep_param"][3] # repulsion from shepherds
        self.p4 = param["sheep_param"][4] # noise
        self.position = np.array([0, 0])
        self.velocity = np.array([0, 0])
        self.main_velocity = np.array([0, 0])
        self.limit = param["sheep_param_limit"] # limit, if distance is smaller than limit, see it as a limit to calculate
        self.prior_position = None
        self.reset(param, i,  trial)
    
    ''' Reset only when initializing '''
    def reset(self, param, i, trial):
        self.gen_init_sheep_position(param, i, trial)
        self.velocity = np.array([0, 0])
        self.v1, self.v2, self.v3, self.v4 = np.array([0, 0]), np.array([0, 0]), np.array([0, 0]), np.array([0, 0])
        self.velocity_list = [self.v1, self.v2, self.v3, self.v4]

    def gen_init_sheep_position(self, param, i, trial):
        random.seed(i + trial) # # trail is used to set seed for random
        if "flock_number" in param:
            num = 0
            sum = 0
            for index in range(0,len(param['sheep_init_num'])):
                num = param['sheep_init_num'][index]
                if i < sum + num: break
                else: sum = sum + num

            base_position = np.array(param["sheep_init_pos_base"][index])
            r = math.sqrt(random.uniform(0, param["sheep_init_pos_radius"][index] ** 2))    
        else:
            base_position = np.array(param["sheep_init_pos_base"])
            r = math.sqrt(random.uniform(0, param["sheep_init_pos_radius"] ** 2))    
        
        theta = random.uniform(-math.pi, math.pi)        
        self.position = base_position + np.array([r * math.cos(theta), r * math.sin(theta)])

    def calculate_velocity(self, sheeps, shepherds):
        u1, u2, u3 = np.array([0,0]), np.array([0,0]), np.array([0,0])
        if len(sheeps) != 0:
            for other in sheeps:
                # tmp: separation + cohesion
                tmp = other.position - self.position
                if np.linalg.norm(tmp) < self.limit: tmp = tmp / np.linalg.norm(tmp) * self.limit
                u1 = u1 + self.p1_c * tmp / np.linalg.norm(tmp) - self.p1_s * tmp / np.power(np.linalg.norm(tmp), 3) 
                
                
                # alignment
                tmp = other.velocity
                if np.linalg.norm(tmp) > 0:
                    u2 = u2 + self.p2 * tmp / np.linalg.norm(tmp)

            self.v1 = u1 / len(sheeps)
            self.v2 = u2 / len(sheeps)

        if len(shepherds) != 0:
            for other in shepherds:     
                tmp = other.position - self.position
                    
                if np.linalg.norm(tmp) > self.limit:
                    u3 = u3 + self.p3 * tmp / np.power(np.linalg.norm(tmp), 3)      
                else:
                    tmp = tmp / np.linalg.norm(tmp) * self.limit
                    u3 = u3 + self.p3 * tmp / (np.power(np.linalg.norm(tmp), 2) * self.limit)

            self.v3 = - u3 / len(shepherds) # repulsion
    
        self.v4 = np.random.uniform(-self.p4,self.p4) * self.noise() # double random
    
    ''' 
    Additional noise for movements
    '''
    def noise(self):    
        u = np.random.rand(1,2) # Continuous uniform distribution
        noise = u[0] / np.linalg.norm(u[0])
        return noise
    
    ''' 
    Detect range 
    threshold self.R
    '''
    def agents_in_region(self, agents):
        in_agents = []
        for other in agents:
            d = np.linalg.norm(other.position - self.position)
            if d < self.R and d != 0:
                in_agents.append(other)
        return in_agents

    ''' 
    Update by considering all forces
    Main function 
    '''
    def update(self, sheeps, shepherds):
        self.prior_position = self.position
        self.position = self.position + self.velocity
        
        near_sheeps = self.agents_in_region(sheeps)
        near_shepherds = self.agents_in_region(shepherds)
        self.calculate_velocity(near_sheeps, near_shepherds) # self.v1, self.v2, self.v3, self.v4

        self.velocity = self.v1 + self.v2 + self.v3 + self.v4
        self.main_velocity = self.v1
        self.velocity_list = [self.v1, self.v2, self.v3, self.v4]

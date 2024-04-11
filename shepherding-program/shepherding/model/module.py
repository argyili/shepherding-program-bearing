import math
import random
import numpy as np
import random

def gen_init_shepherd_position(i, param, trial):
    random.seed(i + trial*100)
    base_position = np.array(param['shepherd_init_pos_base'])
    
    # If selected: Generate shepherd's initial position in a circular ring within a hollowed vacuum
    r = 0
    if 'shepherd_init_pos_vacuum' in param:
        r = math.sqrt(random.uniform((param['shepherd_init_pos_vacuum'] ** 2), param['shepherd_init_pos_radius'] ** 2))
    else:
        r = math.sqrt(random.uniform(0, param['shepherd_init_pos_radius'] ** 2))

    # If selected: Restrict shepherd initial position partly in the circular ring
    theta = random.uniform(-math.pi, math.pi)    
    if 'shepherd_init_direction' in param:
        # From top
        if param['shepherd_init_direction'] == 'top_right':
            if theta < -0.25*math.pi or  theta > 0.75*math.pi:
                theta -= math.pi
        # From bottom
        if param['shepherd_init_direction'] == 'bottom_left':
            if theta > -0.25*math.pi and theta < 0.75*math.pi:
                theta -= math.pi
    return base_position, r, theta

def reset_shepherd(self, param, i, trial):
    # param
    self.no = i
    self.R = param['shepherd_range'] 
    self.param = param
    self.model = param['shepherd_method']
    self.goal = param['goal']
    self.goal_radius = param['goal_radius']
    self.sheeps = []
    self.target_sheep = None
    self.velocity = np.array([0, 0])
    self.main_velocity = np.array([0, 0])
    self.target_position = None # Target position based on the target sheep
    self.min_dis_from_sheep = 0
    self.max_dis_from_sheep = 0 # Movement distance in one time
    self.step_distance = 0
    self.is_success = False
    self.alive = True
    if 'shepherd_angle' in param:
        self.angle = param['shepherd_angle']
    if 'shepherd_death_rate' in param:
        self.deathrate = param['shepherd_death_rate']
        self.backrate = param['shepherd_backlife_rate']

    base_position, r, theta = gen_init_shepherd_position(i, param, trial)
    self.position = base_position + np.array([r * math.cos(theta), r * math.sin(theta)])
    
    return self
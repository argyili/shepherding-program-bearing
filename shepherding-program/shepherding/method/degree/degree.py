import math
import numpy as np
import copy

# Shepherding method
class Degree_Shepherd:
    def __init__(self, param):
        self.NAME = 'degree'
        self.sheeps = []
        self.shepherds = []
        
        self.judge = False
        if 'judge_radius' in param:
            if param['judge_radius'] == 'True':
                self.judge = True
                self.r = param['threshold']
        
    ''' Update information every time before updating target '''
    def update(self, sheeps, shepherds, step):
        self.sheeps = sheeps
        self.shepherds = shepherds
        self.update_target_sheep(step)

    def reset(self):
        self.flock_center = np.array([0, 0])
        self.flock_size = 0
        self.flock_sheep_num = 0

    def check_sign(self, deg1, deg2):
        if (deg1 >= 0 and deg2 >= 0) or (deg1 < 0 and deg2 < 0):
            return True
        else:
            return False
    
    def rounding(self, shepherd, num):
        if shepherd.precision != 0:
            num = num - num % shepherd.precision

        return num

    '''
    Counterclockwise direction from p1 to p2 
    Result ranges (from 0 to pi counterclockwise) to (from -pi to 0 clockwise)    
    '''
    # There can be many methods to calculate angle, another method can be np.cross
    def angle_between(self, shepherd, p1, p2):
        ang1 = np.arctan2(*p1[::-1])
        ang1 = self.rounding(shepherd, ang1)
        ang2 = np.arctan2(*p2[::-1])
        ang2 = self.rounding(shepherd, ang2)
        radian = (ang2 - ang1) % (2 * np.pi)
        if radian > np.pi:
            radian = radian - 2 * np.pi
        return radian
    
    # Rotate a 2D vector counterclockwise
    # angle is radian
    def rotate_point(self, vector, angle):
        x = vector[0]
        y = vector[1]
        # Confirm angle is radian
        angle_rad = angle

        # Compute sine and cosine of the angle
        cos_theta = math.cos(angle_rad)
        sin_theta = math.sin(angle_rad)

        # Apply rotation matrix
        new_x = x * cos_theta - y * sin_theta
        new_y = x * sin_theta + y * cos_theta

        new_vector = np.array([new_x, new_y])
        return new_vector
    
    '''
    Use occlusion. Agent represents either sheep or shepherd. 
    '''
    def check_visible(self, sorted_agents, agent, shepherd, step):
        # Limit sensing distance
        d_sheep = np.linalg.norm(agent.position - shepherd.position)
        if d_sheep > shepherd.R or d_sheep == 0: return False
        if sorted_agents == None: return False

        dir = (agent.position - shepherd.position) / np.linalg.norm(agent.position - shepherd.position)
        for i in range(len(sorted_agents)):
            if agent.no == sorted_agents[i].no: break
            base_dir = (sorted_agents[i].position - shepherd.position) / np.linalg.norm(sorted_agents[i].position - shepherd.position)
            if abs(math.degrees(self.angle_between(shepherd, dir, base_dir))) < shepherd.thres_occlusion: # self.angle is radian (0 - pi) 
                return False
            
        return True

    def calculate_visible_agents(self, sheeps, shepherds, shepherd, step):
        other_shepherds = copy.deepcopy(shepherds)
        for one_shepherd in other_shepherds:
            if np.array_equal(one_shepherd.position, shepherd.position):
                other_shepherds.remove(one_shepherd)
        
        agents = sheeps + other_shepherds # occlusion for both types of agents
        sorted_sheeps = sorted(sheeps, key=lambda k: (k.position[0] - shepherd.position[0]) ** 2 + (k.position[1] - shepherd.position[1]) ** 2)
        sorted_shepherds = sorted(shepherds, key=lambda k: (k.position[0] - shepherd.position[0]) ** 2 + (k.position[1] - shepherd.position[1]) ** 2)
        sorted_agents = sorted(agents, key=lambda k: (k.position[0] - shepherd.position[0]) ** 2 + (k.position[1] - shepherd.position[1]) ** 2)
        
        visible_sheeps = []
        visible_shepherds = []
        for j in range(len(sorted_sheeps)):
            sheep = sorted_sheeps[len(sorted_sheeps) - 1 - j]
            if not self.check_visible(sorted_agents, sheep, shepherd, step): continue
            visible_sheeps.append(sheep)
        
        for j in range(len(sorted_shepherds)):
            shepherd_j = sorted_shepherds[len(sorted_shepherds) - 1 - j]
            if not self.check_visible(sorted_agents, shepherd_j, shepherd, step): continue
            visible_shepherds.append(shepherd_j)

        return visible_sheeps, visible_shepherds

    # From one shepherd to other shepherds
    def get_directions_to_other_shepherds(self, shepherd, shepherds):
        dirs_to_shepherds = {'shepherd': [], 'direction': []} # other shepherd, from this shepherd to that shepherd (other shepherd)
        if shepherds == [] or len(shepherds) == 0:
            return dirs_to_shepherds
        for i in range(len(shepherds)): 
            if np.linalg.norm(shepherds[i].position - shepherd.position) != 0:
                dirs_to_shepherds_i = (shepherds[i].position - shepherd.position) / np.linalg.norm(shepherds[i].position - shepherd.position)
                dirs_to_shepherds['shepherd'].append(shepherds[i])
                dirs_to_shepherds['direction'].append(dirs_to_shepherds_i)
        return dirs_to_shepherds
    
    # From one shepherd to sheeps
    def get_directions_to_sheeps(self, shepherd, sheeps, step): # base: from shepherd to goal
        shd_goal_unit_v = (shepherd.goal - shepherd.position) / np.linalg.norm(shepherd.goal - shepherd.position)
        base_goal = shd_goal_unit_v
        
        dirs_to_sheeps = []
        for i in range(len(sheeps)): 
            if np.linalg.norm(sheeps[i].position - shepherd.position) != 0:
                dirs_to_sheeps_i = (sheeps[i].position - shepherd.position) / np.linalg.norm(sheeps[i].position - shepherd.position)
                dirs_to_sheep_list = {'position': sheeps[i].position, 'direction': dirs_to_sheeps_i, 'angle': self.angle_between(shepherd, base_goal, dirs_to_sheeps_i), 'base': base_goal} # radian from -pi 
                dirs_to_sheeps.append(dirs_to_sheep_list)
        return dirs_to_sheeps

    def divide_flocks(self, shepherd, dirs_to_sheeps, step):
        flock_list = []
        dirs_to_sheeps = sorted(dirs_to_sheeps, key = lambda i: i['angle'])
        thres_flock_interval = shepherd.thres_flock_interval
        
        i = 0
        tmp_sheep_list = []
        continue_flag = False # in the same list with the last agent
        while i < len(dirs_to_sheeps):
            if i == 0 or continue_flag == False:
                continue_flag = True
                tmp_sheep_list.append(dirs_to_sheeps[i])
                i += 1
                continue

            if dirs_to_sheeps[i]['angle'] < dirs_to_sheeps[i - 1]['angle'] + thres_flock_interval:
                tmp_sheep_list.append(dirs_to_sheeps[i])
                i += 1
            else:
                continue_flag = False
                flock_list.append(tmp_sheep_list)                
                tmp_sheep_list = []
        
        if tmp_sheep_list != []:
            continue_flag = False
            flock_list.append(tmp_sheep_list)                            
            tmp_sheep_list = []

        if len(flock_list) >= 2:      
            # reverse direction circling, merge if meeting the contion
            if abs(flock_list[0][0]['angle'] + 2*math.pi - flock_list[-1][-1]['angle']) < thres_flock_interval:
                flock_tmp_last = flock_list[0]
                flock_tmp_last = sorted(flock_tmp_last, key = lambda i: abs(i['angle']))
                flock_tmp_first = flock_list[-1]
                flock_tmp_first = sorted(flock_tmp_first, key = lambda i: abs(i['angle']), reverse=True)
                flock_list[0] = flock_tmp_last + flock_tmp_first # last+first
                flock_list.pop()
                
        return flock_list
    
    def select_one_flock(self, shepherd, flock_list, step):
        shd_goal_unit_v = (shepherd.goal - shepherd.position) / np.linalg.norm(shepherd.goal - shepherd.position)
        base_goal = shd_goal_unit_v

        max_abs_angle = 0
        selected_flock = flock_list[0]
        for flock in flock_list:
            dir_sheep_avg = (flock[-1]['direction'] + flock[0]['direction']) / np.linalg.norm(flock[-1]['direction'] + flock[0]['direction'])
            angle_sheep_avg = self.angle_between(shepherd, base_goal, dir_sheep_avg)
            if max_abs_angle < abs(angle_sheep_avg): 
                max_abs_angle = abs(angle_sheep_avg)
                selected_flock = flock
                
        dir_sheep_avg = (selected_flock[-1]['direction'] + selected_flock[0]['direction']) / np.linalg.norm(selected_flock[-1]['direction'] + selected_flock[0]['direction'])
        angle_sheep_avg = self.angle_between(shepherd, base_goal, dir_sheep_avg)
        dir_angle_pos = {
            'dir_sheep_left': selected_flock[-1]['direction'],   
            'dir_sheep_right': selected_flock[0]['direction'],
            'dir_sheep_avg': dir_sheep_avg,
            'angle_sheep_left': selected_flock[-1]['angle'],   
            'angle_sheep_right': selected_flock[0]['angle'],
            'angle_sheep_avg': angle_sheep_avg,
            'pos_sheep_left': selected_flock[-1]['position'],
            'pos_sheep_right': selected_flock[0]['position'],
            'pos_sheep_avg': (selected_flock[-1]['position'] + selected_flock[0]['position']) / 2,
            'dir_base_goal': selected_flock[0]['base'],
        } 
        return dir_angle_pos, selected_flock
    
    def shepherd_multi_flock_algorithm(self, shepherd, sheeps, step):
        dirs_to_sheeps = self.get_directions_to_sheeps(shepherd, sheeps, step) # Get directions from this shepherd to sheep
        flock_list = self.divide_flocks(shepherd, dirs_to_sheeps, step) # Divide flocks based on the directions
        dir_angle_pos, selected_flock = self.select_one_flock(shepherd, flock_list, step) # Select one flock to herd now
        return dir_angle_pos, selected_flock

    # Update dir_angle_pos by considering multi shepherds
    def replace_dir_angle_pos(self, shepherd, visible_shepherds, dir_angle_pos, dirs_to_visible_shepherds, step):
        dir_sheep_left = dir_angle_pos['dir_sheep_left']
        dir_sheep_right = dir_angle_pos['dir_sheep_right']
        dir_sheep_avg = dir_angle_pos['dir_sheep_avg']
        
        shepherd.count_shepherd_left = 0
        shepherd.count_shepherd_right = 0
        
        # Base shepherd itself
        for i in range(len(dirs_to_visible_shepherds['shepherd'])):
            angle_between_sheep_avg_and_sheep_right = self.angle_between(shepherd, dir_sheep_avg,dir_sheep_right)
            angle_between_sheep_avg_and_sheep_left = self.angle_between(shepherd, dir_sheep_avg,dir_sheep_left)
            angle_between_sheep_avg_and_shepherd_i = self.angle_between(shepherd, dir_sheep_avg,dirs_to_visible_shepherds['direction'][i])
            
            visible_sheeps_i, visible_shepherds_i = self.calculate_visible_agents(self.sheeps, self.shepherds, dirs_to_visible_shepherds['shepherd'][i], step)
            if visible_sheeps_i == []: continue
            shepherd_i_dir_angle_pos, selected_flock = self.shepherd_multi_flock_algorithm(dirs_to_visible_shepherds['shepherd'][i], visible_sheeps_i, step)
            angle_between_shepherd_and_sheep_avg_and_between_shepherd_i_and_sheep_i_avg = self.angle_between(shepherd, dir_sheep_avg, shepherd_i_dir_angle_pos['dir_sheep_avg'])
            
            if abs(angle_between_shepherd_and_sheep_avg_and_between_shepherd_i_and_sheep_i_avg) < shepherd.thres_multi_1:
                if angle_between_sheep_avg_and_shepherd_i < 0 and abs(angle_between_sheep_avg_and_shepherd_i-angle_between_sheep_avg_and_sheep_right) < shepherd.thres_multi_2:
                    shepherd.count_shepherd_right += 1            
                if angle_between_sheep_avg_and_shepherd_i > 0 and abs(angle_between_sheep_avg_and_shepherd_i-angle_between_sheep_avg_and_sheep_left) < shepherd.thres_multi_2:
                    shepherd.count_shepherd_left += 1
        
        angle_sheep_avg = dir_angle_pos['angle_sheep_avg']
        # Rotate outward dir_shepherd_left/right 
        if abs(angle_sheep_avg) > shepherd.thres_orient: # Stage 1
            dir_angle_pos['dir_shepherd_right'] = self.rotate_point(dir_sheep_right, -shepherd.thres_rotate_1)
            dir_angle_pos['dir_shepherd_left'] = self.rotate_point(dir_sheep_left, shepherd.thres_rotate_1)
        else: # Stage 2
            dir_angle_pos['dir_shepherd_right'] = self.rotate_point(dir_sheep_right, -shepherd.thres_rotate_2)     
            dir_angle_pos['dir_shepherd_left'] = self.rotate_point(dir_sheep_left, shepherd.thres_rotate_2)
        return shepherd, dir_angle_pos
    
    ''' 
    Judge distance
    Get the central position of sheep flock
    '''
    def get_flock_center(self, shepherd):
        self.flock_center = np.array([0, 0])
        for i in range(len(self.sheeps)):
            # limited detect distance
            d_shepherd = np.linalg.norm(self.sheeps[i].position - shepherd.position)
            if d_shepherd > self.R: continue
            self.flock_center = np.add(self.flock_center, self.sheeps[i].position)
        self.flock_center = np.divide(self.flock_center, len(self.sheeps))
                    
    def update_target_sheep(self, step):
        self.reset()
        sheeps = self.sheeps
        for i in range(len(self.shepherds)): 
            shepherds = self.shepherds
            shepherd = self.shepherds[i]
            visible_sheeps, visible_shepherds = self.calculate_visible_agents(sheeps, shepherds, shepherd, step)
            shepherd.v1 = np.array([0,0])
            shepherd.v2 = np.array([0,0])
            shepherd.v3 = np.array([0,0])
            if visible_sheeps == []: continue
            
            # dir_angle_pos = self.get_two_sides_of_sheep_towawrds_shepherd(shepherd)
            dir_angle_pos, selected_flock = self.shepherd_multi_flock_algorithm(shepherd, visible_sheeps, step)

            dirs_to_visible_shepherds = self.get_directions_to_other_shepherds(shepherd, visible_shepherds)
            shepherd, dir_angle_pos = self.replace_dir_angle_pos(shepherd, visible_shepherds, dir_angle_pos, dirs_to_visible_shepherds, step)
            
            shepherd.target_sheep = None 
            shepherd.target_position = [] # no practical use, only for visualization
            
            dir_sheep_right = dir_angle_pos['dir_sheep_right']
            dir_sheep_left = dir_angle_pos['dir_sheep_left']
            dir_sheep_avg = dir_angle_pos['dir_sheep_avg']            
            angle_sheep_right = dir_angle_pos['angle_sheep_right']
            angle_sheep_left = dir_angle_pos['angle_sheep_left']
            angle_sheep_avg = dir_angle_pos['angle_sheep_avg']
            pos_sheep_right = dir_angle_pos['pos_sheep_right']
            pos_sheep_left = dir_angle_pos['pos_sheep_left']
            pos_sheep_avg = dir_angle_pos['pos_sheep_avg']
            base_goal = dir_angle_pos['dir_base_goal']
            
            dir_shepherd_right = dir_angle_pos['dir_shepherd_right']
            dir_shepherd_left = dir_angle_pos['dir_shepherd_left']

            # Stage 1: Orientation
            if abs(angle_sheep_avg) > shepherd.thres_orient:
                shepherd.flag = 0      
                if abs(angle_sheep_left) > abs(angle_sheep_right):
                    shepherd.v1 = dir_shepherd_left
                    shepherd.target_position = pos_sheep_left
                else:
                    shepherd.v1 = dir_shepherd_right
                    shepherd.target_position = pos_sheep_right
                    
            # Stage 2: Switching movement
            else:
                if shepherd.flag == 0: # initial, decide left or right direction
                    if abs(angle_sheep_left) > abs(angle_sheep_right):
                        shepherd.v1 = dir_shepherd_left
                    else:
                        shepherd.v1 = dir_shepherd_right

                if shepherd.flag == 1: # left last time      
                    if shepherd.count_shepherd_left <= shepherd.count_shepherd_right:
                        # if left enough
                        if abs(angle_sheep_left) < shepherd.thres_switch_2 and self.check_sign(angle_sheep_left, angle_sheep_right):
                            shepherd.v1 = dir_shepherd_right
                        else:
                            shepherd.v1 = dir_shepherd_left
                    else: # turn right
                        shepherd.v1 = dir_shepherd_right
                
                if shepherd.flag == -1: # right last time    
                    if shepherd.count_shepherd_right <= shepherd.count_shepherd_left: 
                        # if right enough
                        if abs(angle_sheep_right) < shepherd.thres_switch_2 and self.check_sign(angle_sheep_left, angle_sheep_right):
                            shepherd.v1 = dir_shepherd_left
                        else:
                            shepherd.v1 = dir_shepherd_right        
                    else: # turn left
                        shepherd.v1 = dir_shepherd_left
                
                # Function together
                if np.array_equal(shepherd.v1, dir_shepherd_left):
                    shepherd.target_position = pos_sheep_left
                    shepherd.flag = 1
                elif np.array_equal(shepherd.v1, dir_shepherd_right):
                    shepherd.target_position = pos_sheep_right
                    shepherd.flag = -1
            
            shepherd.v2 = -base_goal
            shepherd.v3 = -dir_sheep_avg
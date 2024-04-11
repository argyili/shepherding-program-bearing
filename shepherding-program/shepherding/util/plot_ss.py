import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as anim
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import seaborn as sns
import math

'''
Counterclockwise direction from p1 to p2 
Note: radian (0-2pi)
'''
def radian_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    radian = (ang2 - ang1) % (2 * np.pi)
    # angle = radian * 180 / np.pi
    return radian

# Rotate a 2D vector counterclockwise
# angle is radian
def rotate_coord(vector, angle):
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

# Rotate counterclockwise
def draw_rotate_marker(angle):
    triangle_marker = np.array([[-0.5, -0.5], [0, 1], [0.5, -0.5], [-0.5, -0.5]]) # Acute-angled triangle
    triangle_marker_rot = []
    for vector in triangle_marker:
        rotated_vector = rotate_coord(vector, angle)
        triangle_marker_rot.append(rotated_vector)

    triangle_marker_rot = np.array(triangle_marker_rot)
    return triangle_marker_rot

def init_figure():
    '''
    Initilize figure
    '''
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    return fig, ax

def set_ax_length(ax):
    # x,y axis range
    value = 350 # the value for setting the scale
    x_range, y_range = value, value
    x_tick, y_tick = value, value 
    ax.set_xlim(-x_range, x_range)
    ax.set_xticks([-x_tick,x_tick])
    ax.set_ylim(-y_range, y_range)
    ax.set_yticks([-y_tick,y_tick])
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.set_aspect('equal') 
        
''' 
Type 1
Initialize plot line by csv, more obvious 
Draw the initial graph
'''
def plot_init_csv(ax, param, sheeps_pos, shepherds_pos):
    shepherd_colors = ['blue', 'green', 'red', 'purple', 'orange', 'gold', 'brown', 'pink', 'grey', 'cyan'] # maximum 10
    
    sns.set(style='white')
    # Goal
    goal_zone = patches.Circle(param['goal'], param['goal_radius'], ec='k', fc='white', alpha=1)
    ax.add_patch(goal_zone)
    
    # (number of sides, style, rotation)
    # Sheep
    for i in range(len(sheeps_pos)):
        # marker = draw_rotate_marker(0)
        marker = 'o'
        ax.plot(sheeps_pos[i][0], sheeps_pos[i][1], color='k', marker=marker, alpha=0.5, markersize='6') # the initial direction of the triangle is up
    # Shepherd
    for j in range(len(shepherds_pos)):
        # marker = draw_rotate_marker(0)
        marker = 'o'
        ax.plot(shepherds_pos[j][0], shepherds_pos[j][1], marker=marker, alpha=0.8, markersize='9', color=shepherd_colors[j]) # the initial direction of the triangle is up
    
    set_ax_length(ax)

def plot_cmap(list, colors, linewidth):
    list = np.asarray(list)
    cmap = plt.get_cmap(colors)
    norm = Normalize(0, 0.5)
    points = np.array([list[:, 0], list[:, 1]]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[1:], points[:-1]], axis=1)
    lc = LineCollection(segments, cmap=cmap, norm=norm, linewidths=linewidth)
    lc.set_array(np.linspace(0, 1, len(segments)))

    return lc

''' 
Type 2
Initialize trace by csv 
Generate the trace pdf
'''
def plot_trace_csv(ax, param, sheeps_pos_list, shepherds_pos_list):
    shepherd_colors = ['blue', 'green', 'red', 'purple', 'orange', 'gold', 'brown', 'pink', 'grey', 'cyan'] # maximum 10
    sns.set(style='white')
    # Goal
    goal_zone = patches.Circle(param['goal'], param['goal_radius'], ec='k', fc='white', alpha=1)
    ax.add_patch(goal_zone)
    
    sheeps_pos_list = list(map(list, zip(*sheeps_pos_list)))
    shepherds_pos_list = list(map(list, zip(*shepherds_pos_list)))
    for j in range(len(sheeps_pos_list)):
        sheeps_pos_list[j] = np.asarray(sheeps_pos_list[j])
        ax.plot(*sheeps_pos_list[j].T, marker='o', alpha=0.6, markersize='0', color='k', linewidth=1.5)
        
    for j in range(len(shepherds_pos_list)):
        shepherds_pos_list[j] = np.asarray(shepherds_pos_list[j])
        ax.plot(*shepherds_pos_list[j].T, marker='o', alpha=1, markersize='0', color=shepherd_colors[j], linewidth=2.25)     

    set_ax_length(ax)

    
''' 
Type 3
Initiliaze plot each line by csv 
Generate time series of figures to merge into one gif
'''
def plot_graph_csv(ax, param, sheeps_pos, sheeps_vel, shepherds_pos, shepherds_targets_pos, shepherds_vel, shepherds_main_velocity):
    shepherd_colors = ['blue', 'green', 'red', 'purple', 'orange', 'gold', 'brown', 'pink', 'grey', 'cyan'] # maximum 10

    sns.set(style='white')
    # Goal
    goal_zone = patches.Circle(param['goal'], param['goal_radius'], ec='k', fc='white', alpha=1)
    ax.add_patch(goal_zone)
    
    baseline = np.array([0,1]) # up
    # Sheep
    for i in range(len(sheeps_pos)):
        angle = radian_between(baseline, sheeps_vel[i])
        marker = draw_rotate_marker(angle)
        ax.plot(sheeps_pos[i][0], sheeps_pos[i][1], marker=marker, color='k', alpha=0.5, markersize='6', rasterized=True) 
        plt.text(sheeps_pos[i][0], sheeps_pos[i][1], str(int(sheeps_pos[i][0]))+','+str(int(sheeps_pos[i][1])), fontsize='6') 
    
    # Shepherd
    for j in range(len(shepherds_pos)):
        angle = radian_between(baseline, shepherds_vel[j])
        marker = draw_rotate_marker(angle)
        ax.plot(shepherds_pos[j][0], shepherds_pos[j][1], marker=marker, alpha=1, markersize='9', rasterized=True, color=shepherd_colors[j])
        plt.text(shepherds_pos[j][0], shepherds_pos[j][1], j, alpha=1, fontsize='12', ha='center', rasterized=True)
        plt.arrow(shepherds_pos[j][0], shepherds_pos[j][1], shepherds_vel[j][0]*5, shepherds_vel[j][1]*5, head_width=0.5, head_length=0.5, length_includes_head=True, color=shepherd_colors[j])
    
    # Shepherd target
    for j in range(len(shepherds_targets_pos)):
        if isinstance(shepherds_targets_pos[j],np.ndarray):
            ax.plot(shepherds_targets_pos[j][0], shepherds_targets_pos[j][1], 'yx', alpha=1, markersize='6', rasterized=True)
            plt.text(shepherds_targets_pos[j][0], shepherds_targets_pos[j][1], j, alpha=1, fontsize='12', ha='center', rasterized=True)
    
    set_ax_length(ax)

''' Figure out which sheep is target sheep '''
def check_target(sheeps, target_sheep):
    for i in range(len(sheeps)):
        # 2D space with x,y attribute
        if sheeps[i].position[0] == target_sheep.position[0] and sheeps[i].position[1] == target_sheep.position[1]:
            return i 
    return 0

''' 
Write a line into csv in each step
Sequence: 
'''
def write_line_csv(writer, sheeps, shepherds):
    # k for sheep, r for alive shepherds, c for dead shepherds
    s = ['shp_pos:' + str(sheeps[i].position) for i in range(len(sheeps))] 
    s = s + ['shp_vel:' + str(sheeps[i].velocity) for i in range(len(sheeps))] 
    s = s + ['shp_vel_main:' + str(sheeps[i].main_velocity) for i in range(len(sheeps))] 
    for i in range(len(sheeps)):
        s.append(sheeps[i].velocity_list)
    
    s = s + ['shd_pos:' + str(shepherds[i].position) for i in range(len(shepherds))] 
    s = s + ['shd_vel:' + str(shepherds[i].velocity) for i in range(len(shepherds))]
    s = s + ['shd_vel_main:' + str(shepherds[i].main_velocity) for i in range(len(shepherds))]
    for i in range(len(shepherds)):
        s.append(shepherds[i].velocity_list)

    for i in range(len(shepherds)): 
        # Plot special color dot at target sheep
        if shepherds[i].target_position != []:
            s.append('shd_target:' + str(shepherds[i].target_position))
    
    writer.writerow(s)

''' Write last line into csv with a result '''
def write_last_line_csv(writer, result):
    writer.writerow(result)
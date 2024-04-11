import numpy as np
import math
import pandas as pd
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as anim
import os 
import json
import shutil
import seaborn as sns
import imageio
import sys

def findFolder(base):
    path_list = os.listdir(base)
    path_list.sort()  
    for f in path_list:
        path = os.path.join(base, f)
        if not os.path.isdir(path): # if not a folder, ignore it
            continue
        yield base + f + '/'

def load(json_path, complement):
    '''
    Read json
    return dict
    '''
    json_dict = None
    try:
        with open(json_path, 'r') as f:
            json_dict = json.load(f)   
    except Exception:
        pass
    
    try:
        if complement == True:
            json_dict = complement_dict(json_dict)
    except Exception:
        pass
    
    return json_dict

def complement_dict(json_dict):
    '''
    足りないkeyをdefalt.jsonと同じvalueで補完する
    '''
    with open("./config/default.json", 'r') as f:
        default_dict = json.load(f)

    for k in default_dict.keys():
        if k not in json_dict:
            json_dict[k] = default_dict[k]

    return json_dict

def get_param(param_file_path):
    '''
    Get parameters as a dict
    '''
    param = load(param_file_path, complement=False)
    return param

def count_line(file_path):
    with open(file_path) as f:
        for line_count, _ in enumerate(f, 1):
            pass
    return line_count

def read_line(path, idx):
    with open(path, mode='r') as f:
        reader = csv.reader(f)
        # Start from line 1, line 1 not existed
        line_count = 1
        while True:
            if line_count == idx:
                break
            f.readline()
            line_count += 1
        return next(reader)

''' Return last line number and its content '''
def read_last_line(file_path):
    line_count = count_line(file_path)
    return read_line(file_path, line_count)

''' Turn string to colored np.array '''
def str_to_color_nparray(str):
    color = str[0]
    np_str = str[3:-1].split()
    # print("str:{} re:{}".format(str, str[1:-1]))
    l = [float(np_str[i]) for i in range(len(np_str))]
    return  color, np.array(l)
    
def find_min_index(directory_path, shepherd_num):
    file_path = directory_path + "/data/" + "{}_all.csv".format(str(shepherd_num))
    df = pd.read_csv(file_path)

    print('idxmin:' + str(df['step'].idxmin()))
    print('min:' + str(df['step'].min()))

    return df['step'].idxmin()

def cal_success(list):
    length = len(list)
    succ_length = length
    succ_list = []
    for line in list:
        if line[3] == 'False':
            succ_length -= 1
        else:
            succ_list.append(line)
    succ_rate = succ_length / length
    return succ_rate, succ_list

''' 
Integrate trials with same configuration for shepherd number and sheep number
Example: 1,25,farthest_offset,1.0,1199,498186,3252,3731967
'''
def integrate_trial(list):
    res = [None] * 8
    res[0] = list[0][0]
    res[1] = list[0][1]
    res[2] = list[0][2]
    succ_rate, succ_list = cal_success(list)
    # Change to success rate instead of success boolean flag
    res[3] = succ_rate
    if len(succ_list) > 0:
        # step index
        res[4] = sum(int(line[-2]) for line in succ_list) / len(succ_list)
        var_line = []
        for line in succ_list: # only add success one
            var_line.append(int(line[-2]))
        res[5] = np.var(var_line)
        # distance index
        res[6] = sum(int(line[-1]) for line in succ_list) / len(succ_list)
        var_line = []
        for line in succ_list:
            var_line.append(int(line[-1]))
        res[7] = np.var(var_line)
    else:
        res[4] = 0
        res[5] = 0
        res[6] = 0
        res[7] = 0
    
    res[4] = str(math.ceil(res[4]))
    res[5] = str(math.ceil(res[5]))
    res[6] = str(math.ceil(res[6]))
    res[7] = str(math.ceil(res[7]))
    return res

''' Summarize each trial information from the last step at each csv file, repeat for trial number '''
def full_csv(directory_path, shepherd_num, sheep_num, trials):
    with open("{}/data/{}.csv".format(directory_path, shepherd_num), mode='a') as f:
        list=[]
        for trial in trials:
            file_path = "{}/data/{}sh{}tr{}.csv".format(directory_path, shepherd_num, sheep_num, trial)
            line = read_last_line(file_path)
            list.append(line)
        int_list = integrate_trial(list)
        writer = csv.writer(f)
        writer.writerow(int_list)

def copy_trajectory_files(fig_path):
    folder_list = fig_path.rsplit('/',5)
    destination_init_path = folder_list[0] + '/fig/' + folder_list[1] + '-' + folder_list[2] + '-' + folder_list[3] + '-' + folder_list[5] + '-init.svg'
    destination_trace_path = folder_list[0] + '/fig/'  + folder_list[1] + '-' + folder_list[2] + '-' + folder_list[3] + '-' + folder_list[5] + '-trajectory.svg'
    source_init_path = fig_path + '-gen.svg'
    source_trace_path = fig_path.rsplit('/',2)[0] +'/gif/' + fig_path.rsplit('/',2)[2] + '-gen.svg'
    if not os.path.exists(folder_list[0] + '/fig/'):
        os.makedirs(folder_list[0] + '/fig/')
    shutil.copy(source_init_path, destination_init_path)
    shutil.copy(source_trace_path, destination_trace_path)
    
''' Draw one trace gif through graphs based on the minimum trace '''
''' shepherd number, sheep number and trial number are all above 0 '''
def first_graph_plot(directory_path, shepherd_num, sheep_num, trial_num, param):
    sns.set(style='white')
    
    file_path = directory_path + '/data/' + '{}sh{}tr{}.csv'.format(str(shepherd_num), str(sheep_num), str(trial_num))
    with open(file_path) as f:
        reader = csv.reader(f, delimiter=',')
        # For trace
        sheeps_pos = []
        shepherds_pos = []
        index = 0
        # row_num = 0
        log_png_path = directory_path + '/png/{}sh{}tr{}'.format(str(shepherd_num), str(sheep_num), str(trial_num))
        if not os.path.exists(log_png_path):
            os.makedirs(log_png_path)
        for row in reader:
            # For trace
            sheeps_pos_row = []
            shepherds_pos_row = []
            for i in range(0, sheep_num):
                pos = str_to_attribute_nparray(row[i])
                sheeps_pos.append(pos)
                sheeps_pos_row.append(pos)
            for i in range(4 * sheep_num, 4 * sheep_num + shepherd_num):   
                pos = str_to_attribute_nparray(row[i])
                shepherds_pos.append(pos)
                shepherds_pos_row.append(pos)

            fig, ax_row = plt.subplots(figsize=(8,8))
            plot_init_csv(ax_row, param, sheeps_pos_row, shepherds_pos_row)
            fig_path = directory_path + '/graph/{}sh{}tr{}-gen.svg'.format(str(shepherd_num), str(sheep_num), str(trial_num))
            plt.tight_layout()
            fig.savefig(fig_path)
            index += 1
            ax_row.clear()
            plt.clf()
            plt.close()
            break
    f.close()
    return

''' 
Genereate one svg trace
time-series
'''
# We judge that Trace does not need velocity 
def gen_one_trace(directory_path, shepherd_num, sheep_num, trial_num, param, max_step):
    sns.set(style='white')

    file_path = directory_path + '/data/' + '{}sh{}tr{}.csv'.format(str(shepherd_num), str(sheep_num), str(trial_num))
    with open(file_path) as f:
        reader = csv.reader(f, delimiter=',')
        line_count = count_line(file_path)
        fig, ax = plt.subplots(figsize=(8,8))
        # For trace
        sheeps_pos_list = []
        sheeps_vel_list = []
        shepherds_pos_list = []
        shepherds_vel_list = []
        shepherds_targets_pos = []
        index = 0
        # row_num = 0
        log_png_path = directory_path + '/png/{}sh{}tr{}'.format(str(shepherd_num), str(sheep_num), str(trial_num))
        if not os.path.exists(log_png_path):
            os.makedirs(log_png_path)
        for row in reader:
            if index >= line_count - 1 or index > max_step: # until the second last line
                break
            # For trace
            sheeps_pos_row = []
            sheeps_vel_row = []
            
            shepherds_pos_row = []
            shepherds_vel_row = []
            shepherds_targets_pos_row = []
            
            # sheep
            length = 0
            for i in range(length, sheep_num):
                value = str_to_attribute_nparray(row[i])
                sheeps_pos_row.append(value)
            
            length = sheep_num
            for i in range(length, length+sheep_num):
                pos = str_to_attribute_nparray(row[i])
                sheeps_vel_row.append(pos)
            
            # shepherd
            length = 4*sheep_num
            for i in range(length, length+shepherd_num):
                pos = str_to_attribute_nparray(row[i])
                shepherds_pos_row.append(pos)
            
            length = 4*sheep_num + shepherd_num
            for i in range(length, length + shepherd_num):                    
                value = str_to_attribute_nparray(row[i])
                shepherds_vel_row.append(value)
            
            length = 4*sheep_num + 4*shepherd_num
            for i in range(length, length + shepherd_num):
                pos = str_to_attribute_nparray(row[i])
                shepherds_targets_pos_row.append(pos)

            sheeps_pos_list.append(sheeps_pos_row)
            shepherds_pos_list.append(shepherds_pos_row)
            shepherds_targets_pos.append(shepherds_targets_pos_row)
            index+=1

        plot_trace_csv(ax, param, sheeps_pos_list, shepherds_pos_list)
        plt.text(0.85, 0.06, 't=' + str(index-1), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=32)
        fig_path = directory_path + '/gif/{}sh{}tr{}-gen.svg'.format(str(shepherd_num), str(sheep_num), str(trial_num))
        # fig_path = directory_path + '/gif/{}sh{}tr{}.png'.format(str(shepherd_num), str(sheep_num), str(trial_num))
        plt.tight_layout()
        fig.savefig(fig_path)
        ax.clear()
        plt.clf()
        plt.close()
    f.close()

''' 
Genereate one gif for all traces
Consume time a lot
'''
def gen_one_gif(directory_path, shepherd_num, sheep_num, trial_num, param, max_step):
    sns.set(style='white')
    file_path = directory_path + '/data/' + '{}sh{}tr{}.csv'.format(str(shepherd_num), str(sheep_num), str(trial_num))
    with open(file_path) as f:
        reader = csv.reader(f, delimiter=',')
        mreader = list(reader)
        line_count = count_line(file_path)
        fig, ax = plt.subplots(figsize=(8,8))
        
        interval = 10 # set interval to make gif quick
        log_png_path = directory_path + '/png/{}sh{}tr{}'.format(str(shepherd_num), str(sheep_num), str(trial_num))
        if not os.path.exists(log_png_path):
            os.makedirs(log_png_path)
        for index in range(0,len(mreader),interval):
            row = mreader[index]
            if index >= line_count - 1 or index > max_step: # until the second last line
                break
            
            # For trace
            sheeps_pos_row = []
            sheeps_vel_row = []
            sheeps_main_vel_row = []
            sheeps_vel_list_row = []
            
            shepherds_pos_row = []
            shepherds_vel_row = []
            shepherds_main_vel_row = []
            shepherds_vel_list_row = []
            
            shepherds_targets_pos_row = []
            
            length = 0
            for i in range(length, sheep_num):
                value = str_to_attribute_nparray(row[i])
                sheeps_pos_row.append(value)
            
            length = sheep_num
            for i in range(length, length + sheep_num):                    
                value = str_to_attribute_nparray(row[i])
                sheeps_vel_row.append(value)
            
            length = 2*sheep_num
            for i in range(length, length + sheep_num):                    
                value = str_to_attribute_nparray(row[i])
                sheeps_main_vel_row.append(value)
                
            length = 3*sheep_num
            for i in range(length, length + sheep_num):                    
                sheeps_vel_list_row.append(row[i])
            
            # shepherd
            length = 4*sheep_num
            for i in range(length, length + shepherd_num):
                value = str_to_attribute_nparray(row[i])
                shepherds_pos_row.append(value)
            
            length = 4*sheep_num + shepherd_num
            for i in range(length, length + shepherd_num):                    
                value = str_to_attribute_nparray(row[i])
                shepherds_vel_row.append(value)
            
            length = 4*sheep_num + 2*shepherd_num
            for i in range(length, length + shepherd_num):                    
                value = str_to_attribute_nparray(row[i])
                shepherds_main_vel_row.append(value)
            
            length = 4*sheep_num + 3*shepherd_num
            for i in range(length, length + shepherd_num):                    
                shepherds_vel_list_row.append(row[i])

            # shepherd target
            length = 4*sheep_num + 4*shepherd_num
            for i in range(length, len(row)):
                value = str_to_attribute_nparray(row[i])
                shepherds_targets_pos_row.append(value)

            fig, ax_row = plt.subplots(figsize=(8,8))
            # draw graph at one time
            plot_graph_csv(ax_row, param, sheeps_pos_row, sheeps_vel_row, shepherds_pos_row, shepherds_targets_pos_row, shepherds_vel_row, shepherds_main_vel_row)
            plt.text(0.85, 0.06, 't=' + str(index), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=32)
            fig_path = log_png_path + '/{}-gen.png'.format(str(index))
            fig.savefig(fig_path)
            ax_row.clear()
            plt.clf()
            plt.close()
        generate_gif_csv(log_png_path, directory_path + '/gif/{}sh{}tr{}-gen.gif'.format(str(shepherd_num), str(sheep_num), str(trial_num)), index,interval)
    f.close()
    
''' Turn string to colored np.array '''
def str_to_attribute_nparray(str):
    array = str.split(':',1)
    attribute = array[0]
    np_str = array[1][1:-1].split()

    l = [float(np_str[i]) for i in range(len(np_str))]
    return np.array(l)

def generate_gif_csv(png_path, gif_file_path, frame, interval):
    ''' Generate gif by existed graphs '''
    frames_path = png_path + '/{i}-gen.png'
    with imageio.get_writer(gif_file_path, mode='I', fps=10) as writer:
        for i in range(0,frame, interval):
            writer.append_data(imageio.imread(frames_path.format(i=i)))
        
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
        # ax.plot(sheeps_pos[i][0], sheeps_pos[i][1], color='k', marker=(3,0,0), alpha=0.5, markersize='80', rasterized=True) # the initial direction of the triangle is up
        ax.plot(sheeps_pos[i][0], sheeps_pos[i][1], color='k', marker='o', alpha=0.5, markersize='6') # the initial direction of the triangle is up

    # Shepherd
    for j in range(len(shepherds_pos)):
        # ax.plot(shepherds_pos[j][0], shepherds_pos[j][1], marker='o', alpha=0.6, markersize='9', color=shepherd_colors[j]) # the initial direction of the triangle is up
        ax.plot(shepherds_pos[j][0], shepherds_pos[j][1], marker='o', alpha=0.6, markersize='9', color=shepherd_colors[j]) # the initial direction of the triangle is up
    
    set_ax_length(ax)


''' 
Type 2
Initialize trace by csv 
Generate the trace svg
'''
def plot_trace_csv(ax, param, sheeps_pos_list, shepherds_pos_list):
    shepherd_colors = ['blue', 'green', 'red', 'purple', 'orange', 'gold', 'brown', 'pink', 'grey', 'cyan'] # maximum 10
    sns.set(style='white')
    # Goal
    goal_zone = patches.Circle(param['goal'], param['goal_radius'], ec='k', fc='white', alpha=1)
    ax.add_patch(goal_zone)
    
    # transposed = list(zip(*data))
    # to [(1, 5, 9), (2, 6, 10), (3, 7, 11), (4, 8, 12)]
    # where the symbol * unpacks or expands the elements (reverse)
    # map unit type to list
    sheeps_pos_list = list(map(list, zip(*sheeps_pos_list)))
    shepherds_pos_list = list(map(list, zip(*shepherds_pos_list)))
    for j in range(len(sheeps_pos_list)):
        sheeps_pos_list[j] = np.asarray(sheeps_pos_list[j])
        ax.plot(*sheeps_pos_list[j].T, marker='o', alpha=0.5, markersize='0', color='k', rasterized=True, linewidth=1)
    
    for j in range(len(shepherds_pos_list)):
        shepherds_pos_list[j] = np.asarray(shepherds_pos_list[j])
        ax.plot(*shepherds_pos_list[j].T, marker='o', alpha=1, markersize='0', color=shepherd_colors[j], rasterized=True, linewidth=2)    

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
    
    baseline = np.array([1,0])
    # Sheep
    for i in range(len(sheeps_pos)):
        angle = angle_between(baseline, sheeps_vel[i])
        ax.plot(sheeps_pos[i][0], sheeps_pos[i][1], marker=(3,0,angle), color='k', alpha=0.5, markersize='8', rasterized=True) 
        plt.text(sheeps_pos[i][0], sheeps_pos[i][1], str(int(sheeps_pos[i][0]))+','+str(int(sheeps_pos[i][1])), fontsize='5') 
        
    # Shepherd
    for j in range(len(shepherds_pos)):
        angle = angle_between(baseline, shepherds_vel[j])
        ax.plot(shepherds_pos[j][0], shepherds_pos[j][1], marker=(3,0,angle), alpha=1, markersize='12', rasterized=True, color=shepherd_colors[j])
        plt.text(shepherds_pos[j][0], shepherds_pos[j][1], j, alpha=1, fontsize='12', ha='center', rasterized=True)
        plt.text(shepherds_pos[j][0], shepherds_pos[j][1], str(int(shepherds_pos[j][0]))+','+str(int(shepherds_pos[j][1])), fontsize='5') 
        plt.arrow(shepherds_pos[j][0], shepherds_pos[j][1], shepherds_vel[j][0]*5, shepherds_vel[j][1]*5, head_width=0.5, head_length=0.5, length_includes_head=True, color=shepherd_colors[j])
        plt.arrow(shepherds_pos[j][0], shepherds_pos[j][1], shepherds_main_velocity[j][0]*5, shepherds_main_velocity[j][1]*5, head_width=0.5, head_length=0.5, length_includes_head=True, color='blue')
    
    # Shepherd target
    for j in range(len(shepherds_targets_pos)):
        ax.plot(shepherds_targets_pos[j][0], shepherds_targets_pos[j][1], 'yx', alpha=1, markersize='6', rasterized=True)
        plt.text(shepherds_targets_pos[j][0], shepherds_targets_pos[j][1], j, alpha=1, fontsize='12', ha='center', rasterized=True)
    
    set_ax_length(ax)
    
def iterate(directory_path, shepherd_num):
    sns.set(style='white')
    param_path = str(directory_path) + str('setting.json')
    print(param_path)
    param = get_param(param_path)

    shepherds = range(param["shepherd_number"][0], param["shepherd_number"][1] + 1)
    sheeps = range(param["sheep_number"][0], param["sheep_number"][1] + 1)
    trials = range(param["trial_number"])

    # shepherd_num = 3
    # shepherd_num = 5
    # shepherd_num = 7
    # shepherd_num = shepherds[0]
    sheep_num = sheeps[0]
    trial_num = trials[0]
    
    data = []
    df1 = pd.DataFrame(data, columns=['shepherd','sheep','model','rate','step','distance','noise'])
    df2 = pd.DataFrame(data, columns=['shepherd','sheep','model','rate','step','distance','noise'])

    first_graph_plot(directory_path, shepherd_num, sheep_num, trial_num, param)
    gen_one_trace(directory_path, shepherd_num, sheep_num, trial_num, param, 3000)
    # gen_one_gif(directory_path, shepherd_num, sheep_num, trial_num, param, 3000)
    
    fig_path = directory_path + 'graph/{}sh{}tr{}'.format(str(shepherd_num), str(sheep_num), str(trial_num))
    copy_trajectory_files(fig_path)
    
'''
Counterclockwise direction from p1 to p2 
Result ranges (from 0 to 360 counterclockwise)    
Note: degree (0-360), no radian (0-2pi)
'''
def angle_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    radian = (ang2 - ang1) % (2 * np.pi)
    angle = radian * 180 / np.pi
    return angle
    
def set_ax_length(ax):
    # x,y axis range
    value = 350 # Flexible
    x_range, y_range = value, value
    x_tick, y_tick = value, value 
    ax.set_xlim(-x_range, x_range)
    ax.set_xticks([-x_tick,x_tick])
    ax.set_ylim(-y_range, y_range)
    ax.set_yticks([-y_tick,y_tick])
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.set_aspect('equal') 
    
    
    
if __name__ == '__main__':
    sns.set(style="white")

    home_path = '/home/li-aiyi/program/shepherding-public/shepherding-log/log'
    
    folder_name = 'config/2023-11-02_shepherd'
    
    """ 1 """
    path_list = []
    folder_path = '1swarm/model1'
    base = home_path + '/' + folder_name + '/' + folder_path + '/'
    path_list.extend(findFolder(base))
    
    # folder_path = '1swarm/model2'
    # base = home_path + '/' + folder_name + '/' + folder_path + '/'
    # path_list.extend(findFolder(base))

    # folder_path = '1swarm/model3'
    # base = home_path + '/' + folder_name + '/' + folder_path + '/'
    # path_list.extend(findFolder(base))

    for path in path_list:
        iterate(path, 3)

    """ 2 """
    path_list = []
    folder_path = '2swarm/model1'
    base = home_path + '/' + folder_name + '/' + folder_path + '/'
    path_list.extend(findFolder(base))

    # folder_path = '2swarm/model2'
    # base = home_path + '/' + folder_name + '/' + folder_path + '/'
    # path_list.extend(findFolder(base))
    
    # folder_path = '2swarm/model3'
    # base = home_path + '/' + folder_name + '/' + folder_path + '/'
    # path_list.extend(findFolder(base))

    for path in path_list:
        iterate(path, 5)
        
    # """ 3 """
    path_list = []
    folder_path = '3swarm/model1'
    base = home_path + '/' + folder_name + '/' + folder_path + '/'
    path_list.extend(findFolder(base))
    
    # folder_path = '3swarm/model2'
    # base = home_path + '/' + folder_name + '/' + folder_path + '/'
    # path_list.extend(findFolder(base))
    
    # folder_path = '3swarm/model3'
    # base = home_path + '/' + folder_name + '/' + folder_path + '/'
    # path_list.extend(findFolder(base))
    
    for path in path_list:
        iterate(path, 7)
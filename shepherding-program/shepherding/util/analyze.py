from itertools import count
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import imageio
import math
from .plot_ss import * 

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
def judge_str_not_none(str):
    target_str = str.split(':',1)[1]
    if target_str == 'None':
        return False
    return True

''' Turn string to colored np.array '''
def str_to_attribute_nparray(str):
    array = str.split(':',1)
    np_str = array[1][1:-1].split()

    l = [float(np_str[i]) for i in range(len(np_str))]
    return np.array(l)

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

''' Output all result data into one result csv  '''
def write_csv(directory_path, file_path, shepherd_nums):
    with open(file_path, mode='a') as f:
        list=[]
        # Add csv head
        list.append(['shepherd', 'sheep', 'method', 'rate', 'step', 'var_step', 'distance', 'var_dis'])
        for shepherd_num in shepherd_nums:
            file_path = '{}/data/{}.csv'.format(directory_path, shepherd_num)
            line = read_last_line(file_path)
            list.append(line)
        writer = csv.writer(f)
        writer.writerows(list)
        
''' Summarize each trial information from the last step at each csv file, repeat for trial number '''
def full_csv(directory_path, shepherd_num, sheep_num, trials):
    with open('{}/data/{}.csv'.format(directory_path, shepherd_num), mode='a') as f:
        list=[]
        for trial in trials:
            file_path = '{}/data/{}sh{}tr{}.csv'.format(directory_path, shepherd_num, sheep_num, trial)
            line = read_last_line(file_path)
            list.append(line)
        int_list = integrate_trial(list)
        writer = csv.writer(f)
        writer.writerow(int_list)

    with open('{}/data/{}_all.csv'.format(directory_path, shepherd_num), mode='a') as f:
        columns=['shepherd','sheep','method','rate','step', 'distance']
        writer = csv.writer(f)
        writer.writerow(columns)
        list=[]
        for trial in trials:
            file_path = '{}/data/{}sh{}tr{}.csv'.format(directory_path, shepherd_num, sheep_num, trial)
            line = read_last_line(file_path)
            writer.writerow(line)
            # list.append(line)
        f.close()

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

def check_min_trace(directory_path, shepherd_num, sheep_num, trial_nums):
    # Set 10000 as default minimum line number
    min_line = 10000
    trial_num = trial_nums[0]
    for i in trial_nums:
        file_path = directory_path + '/data/' + '{}sh{}tr{}.csv'.format(str(shepherd_num), str(sheep_num), str(i))
        cnt = count_line(file_path)
        if cnt < min_line:
            min_line = cnt
            trial_num = i
    return trial_num

def check_max_trace(directory_path, shepherd_num, sheep_num, trial_nums):
    # Set 0 as default maximum line number
    max_line = 0
    trial_num = trial_nums[0]
    for i in trial_nums:
        file_path = directory_path + '/data/' + '{}sh{}tr{}.csv'.format(str(shepherd_num), str(sheep_num), str(i))
        cnt = count_line(file_path)
        if cnt > max_line:
            max_line = cnt
            trial_num = i
    return trial_num

''' Draw all pdf trace through graphs by trace '''
def gen_all_trace(directory_path, shepherd_num, sheep_num, trial_num, param, max_step):
    first_graph_plot(directory_path, shepherd_num, sheep_num, trial_num, param)
    gen_one_trace(directory_path, shepherd_num, sheep_num, trial_num, param, max_step)

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
            fig_path = directory_path + '/graph/{}sh{}tr{}.pdf'.format(str(shepherd_num), str(sheep_num), str(trial_num))
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
Genereate one pdf trace
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
            # Shepherd does not have a target if it does not see anything
            for i in range(length, len(row)):
                if judge_str_not_none(row[i]):
                    value = str_to_attribute_nparray(row[i])
                    shepherds_targets_pos_row.append(value)
                else: 
                    shepherds_targets_pos_row.append(None)

            sheeps_pos_list.append(sheeps_pos_row)
            shepherds_pos_list.append(shepherds_pos_row)
            shepherds_targets_pos.append(shepherds_targets_pos_row)
            index += 1

        plot_trace_csv(ax, param, sheeps_pos_list, shepherds_pos_list)
        plt.text(0.85, 0.06, 't=' + str(index-1), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=32)
        fig_path = directory_path + '/gif/{}sh{}tr{}.pdf'.format(str(shepherd_num), str(sheep_num), str(trial_num))
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
        
        interval = 5 # set interval to make gif slower or slower
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

            # Shepherd target
            length = 4*sheep_num + 4*shepherd_num
            # Shepherd may not have a target if it does not see anything
            for i in range(length, len(row)):
                if judge_str_not_none(row[i]):
                    value = str_to_attribute_nparray(row[i])
                    shepherds_targets_pos_row.append(value)
                else: 
                    shepherds_targets_pos_row.append(None)
    
            fig, ax_row = plt.subplots(figsize=(8,8))
            # draw a graph at each time step
            plot_graph_csv(ax_row, param, sheeps_pos_row, sheeps_vel_row, shepherds_pos_row, shepherds_targets_pos_row, shepherds_vel_row, shepherds_main_vel_row)
            plt.text(0.85, 0.06, 't=' + str(index), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=32)
            fig_path = log_png_path + '/{}.png'.format(str(index))
            fig.savefig(fig_path)
            ax_row.clear()
            plt.clf()
            plt.close()
        generate_gif_csv(log_png_path, directory_path + '/gif/{}sh{}tr{}.gif'.format(str(shepherd_num), str(sheep_num), str(trial_num)), index,interval)
    f.close()

def generate_gif_csv(png_path, gif_file_path, frame, interval):
    ''' Generate gif by existed graphs '''
    frames_path = png_path + '/{i}.png'
    with imageio.get_writer(gif_file_path, mode='I', fps=10) as writer:
        for i in range(0,frame, interval):
            writer.append_data(imageio.imread(frames_path.format(i=i)))
            
''' Draw minimal gif trace through graphs by trace '''
def gen_gifs(directory_path, shepherd_num, sheep_num, trial_num, param, max_step):
    gen_one_trace(directory_path, shepherd_num, sheep_num, trial_num, param, max_step)
    gen_one_gif(directory_path, shepherd_num, sheep_num, trial_num, param, max_step)

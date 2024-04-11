import numpy as np
import math
import pandas as pd
import csv
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import sys
import statistics
import shutil

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
    Read json file
    Return data in dict type 
    '''
    json_dict = None
    try:
        with open(json_path, 'r') as f:
            json_dict = json.load(f)   
    except Exception:
        pass
        
    return json_dict

def write_list(file_path, list):
    '''
    Write list into file
    '''
    with open(file_path, 'w') as f:
        write = csv.writer(f)
        write.writerow(list)
        
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

''' Turn string to colored np.array '''
def judge_str_not_none(str):
    target_str = str.split(':',1)[1]
    if target_str == 'None':
        return False
    return True

''' Turn string to colored np.array '''
def str_to_attribute_nparray(str):
    array = str.split(':',1)
    attribute = array[0]
    np_str = array[1][1:-1].split()

    l = [float(np_str[i]) for i in range(len(np_str))]
    return np.array(l)

def read_file(path):
    list = []
    with open(path, mode='r') as f:
        reader = csv.reader(f)
        # Start from line 1, line 1 not existed
        for row in reader:
            list.append(row)
    f.close()
    return list

def calculate_max_value_list(list):
    max_value_list = []
    for row in list:
        max_value = 0
        for x in row:
            coord_x = np.array(x)
            value = np.linalg.norm(coord_x)
            if value > max_value: max_value = value
        max_value_list.append(max_value)
        
    return max_value_list

def calculate_median_value_list(list):
    mean_value_list = []
    for row in list:
        x_coords = [point[0] for point in row]
        y_coords = [point[1] for point in row]

        median_x = statistics.median(x_coords)
        median_y = statistics.median(y_coords)
        median_2d = (median_x, median_y)
        mean_value_list.append(median_2d)
        
    return mean_value_list

def calculate_dis_to_goal_list(param, list):
    dis_list = []
    goal = param['goal']
    for row in list:
        tmp_list = []
        for x in row:    
            coord = np.array(x)
            dis = np.linalg.norm(coord - goal)
            tmp_list.append(dis)
        dis_list.append(tmp_list)
         
    return dis_list

def calculate_max_dis_to_goal_list(param, list):
    max_dis_list = []
    goal = param['goal']
    for row in list:
        max_dis = 0
        for x in row:    
            coord = np.array(x)
            dis = np.linalg.norm(coord - goal)
            if dis > max_dis: max_dis = dis
        max_dis_list.append(max_dis)
        
    return max_dis_list

def calculate_avg_dis_to_goal_list(param, list):
    avg_dis_list = []
    goal = param['goal']
    for row in list:
        total_dis = 0
        for x in row:
            coord = np.array(x)
            dis = np.linalg.norm(coord - goal)
            total_dis += dis
        avg_dis = total_dis / len(row)
        avg_dis_list.append(avg_dis)

    return avg_dis_list

def calculate_min_dis_to_goal_list(param, list):
    min_dis_list = []
    goal = param['goal']
    for row in list:
        min_dis = sys.maxsize
        for x in row:    
            coord = np.array(x)
            dis = np.linalg.norm(coord - goal)
            if dis < min_dis: min_dis = dis
        min_dis_list.append(min_dis)
        
    return min_dis_list

def calculate_max_difference_list(list):
    max_diff_list = []
    for row in list:
        max_diff = 0
        if len(row) == 1:
            max_diff_list.append(np.linalg.norm(row[0]))
            continue
        for x in row:
            for y in row:
                coord_x = np.array(x)
                coord_y = np.array(y)
                diff = np.linalg.norm(coord_x - coord_y)
                if diff == 0: continue
                if diff > max_diff: max_diff = diff
        max_diff_list.append(max_diff)
        
    return max_diff_list

def calculate_sheep_max_velocity_data(fig_path, sheeps_vel_list):
    sheeps_max_vel_list = calculate_max_value_list(sheeps_vel_list) # mutual distance between sheep
    df = pd.DataFrame(sheeps_max_vel_list)
    csv_path = fig_path+'_sheep-max-velocity.csv'
    df.to_csv(csv_path, index=False)

def calculate_sheep_median_velocity_data(fig_path, sheeps_vel_list):
    sheeps_median_vel_list = calculate_median_value_list(sheeps_vel_list) # mutual distance between sheep
    df = pd.DataFrame(sheeps_median_vel_list)
    csv_path = fig_path+'_sheep-median-velocity.csv'
    df.to_csv(csv_path, index=False)

def calculate_shepherd_max_velocity_data(fig_path, shepherds_vel_list):
    shepherds_max_vel_list = calculate_max_value_list(shepherds_vel_list) # mutual distance between shepherds
    df = pd.DataFrame(shepherds_max_vel_list)
    csv_path = fig_path+'_shepherd-max-velocity.csv'
    df.to_csv(csv_path, index=False)

def calculate_sheep_distance_data(fig_path, sheeps_pos_list):
    sheeps_max_dis_key_list = []
    sheeps_max_dis_list = calculate_max_difference_list(sheeps_pos_list)
    k_s = 0.02 # scale for judging whether the swarm is stable 
    k_g = 0.8 # parameter for suggestion of setting the goal radius
    for i in range(1, len(sheeps_max_dis_list)):
        if abs(float(sheeps_max_dis_list[i]) - float(sheeps_max_dis_list[i-1])) < k_s * float(sheeps_max_dis_list[i-1]):
            sheep_radius = 'sheep diameter:' + str(math.ceil(sheeps_max_dis_list[i]))
            goal_radius = 'goal radius:' + str(math.ceil(k_g * int(sheeps_max_dis_list[i])))
    sheeps_max_dis_key_list.append(sheep_radius)
    sheeps_max_dis_key_list.append(goal_radius)
    df = pd.DataFrame(sheeps_max_dis_list)
    df_key = pd.DataFrame(sheeps_max_dis_key_list)
    csv_path = fig_path+'_sheep-max-distance.csv'
    csv_key_path = fig_path+'_sheep-max-distance_key.csv'
    df.to_csv(csv_path, index=False, header=False)
    df_key.to_csv(csv_key_path, index=False, header=False)
    return df

# Distance from agent to the goal position
def plot_distance_to_goal_graph(fig_path, param, sheeps_pos_list, shepherds_pos_list):
    fig, ax = plt.subplots(figsize=(8,6))

    shepherds_max_dis_to_goal_list = calculate_max_dis_to_goal_list(param, shepherds_pos_list)           
    shepherds_min_dis_to_goal_list = calculate_min_dis_to_goal_list(param, shepherds_pos_list)
    shepherds_avg_dis_to_goal_list = calculate_avg_dis_to_goal_list(param, shepherds_pos_list)
    shepherds_max_df = pd.DataFrame({'distance': shepherds_max_dis_to_goal_list, 'type': 'sheep_max'})
    shepherds_min_df = pd.DataFrame({'distance': shepherds_min_dis_to_goal_list, 'type': 'sheep_min'})
    shepherds_avg_df = pd.DataFrame({'distance': shepherds_avg_dis_to_goal_list, 'type': 'shepherd_avg'})
    
    sheeps_max_dis_to_goal_list = calculate_max_dis_to_goal_list(param, sheeps_pos_list)           
    sheeps_min_dis_to_goal_list = calculate_min_dis_to_goal_list(param, sheeps_pos_list)
    sheeps_avg_dis_to_goal_list = calculate_avg_dis_to_goal_list(param, sheeps_pos_list)
    sheeps_max_df = pd.DataFrame({'distance': sheeps_max_dis_to_goal_list, 'type': 'sheep_max'})
    sheeps_min_df = pd.DataFrame({'distance': sheeps_min_dis_to_goal_list, 'type': 'sheep_min'})
    sheeps_avg_df = pd.DataFrame({'distance': sheeps_avg_dis_to_goal_list, 'type': 'sheep_avg'})
    
    ax.plot(sheeps_avg_df.index, sheeps_avg_df['distance'], label='Curve', linewidth=2, color='grey')
    ax.fill_between(sheeps_avg_df.index, sheeps_min_df['distance'], sheeps_max_df['distance'], alpha=0.3, label='Interval', color='grey')
    ax.plot(shepherds_avg_df.index, shepherds_avg_df['distance'], label='Curve', linewidth=2, color='#1f77b4')
    ax.fill_between(shepherds_avg_df.index, shepherds_min_df['distance'], shepherds_max_df['distance'], alpha=0.3, label='Interval', color='#1f77b4')
    
    ax.set_xticks([0,400,800])
    ax.set_xticklabels(ax.get_xticks(), fontsize=16)
    ax.set_yticks([0,175,350])
    ax.set_ylim([-17.5,362.5])
    ax.set_yticklabels(ax.get_yticks(), fontsize=16)
    
    plt.tight_layout()
    folder_list = fig_path.rsplit('/',5)
    pdf_path = folder_list[0] + '/fig/'+ folder_list[1] + '-' + folder_list[2] + '-' + folder_list[3] + '-' + folder_list[5] + '-distance.pdf'
    if not os.path.exists(folder_list[0] + '/fig/'):
        os.makedirs(folder_list[0] + '/fig/')
    
    fig.savefig(pdf_path)
    ax.clear()
    plt.clf()
    plt.close()

# Plot the length of the swarm shape in each model
def plot_init_length_list(list, name):
    df = pd.DataFrame()
    for directory_path in list:
        print(directory_path)
        sns.set(style='white')
        param_path = str(directory_path) + str('setting.json')
        param = get_param(param_path)
        shepherds = range(param["shepherd_number"][0], param["shepherd_number"][1] + 1)
        sheeps = range(param["sheep_number"][0], param["sheep_number"][1] + 1)
        trials = range(param["trial_number"])

        shepherd_num = shepherds[0]
        sheep_num = sheeps[0]
        trial_num = trials[0]
        csv_file_path = directory_path + 'graph/' + '{}sh{}tr{}_sheep-max-distance.csv'.format(str(shepherd_num), str(sheep_num), str(trial_num))    
        df_tmp = pd.read_csv(csv_file_path)
        df = pd.concat([df, df_tmp], axis=1)

    folder_path = list[0].rsplit('/',3)[0]
    csv_path = folder_path + '/swarm-length'+name+'.csv'
    df.columns = ['1','2','3']
    print(df)
    df.to_csv(csv_path, index=False)

    fig, ax = plt.subplots(figsize=(8,6))
    colors = ['#008744','#1668bd','#c0281c'] # green, blue, red: three colors
    customPalette = sns.set_palette(sns.color_palette(colors))
    sns.lineplot(data=df, linewidth=3, palette=customPalette, dashes=False)

    legend = plt.legend(fontsize=16)
    legend.get_frame().set_facecolor('none')
    for line in legend.get_lines():
        line.set_linewidth(3)
    
    # ax.set_xlim([-10, 310])
    # ax.set_ylim([0, 250])
    ax.set_xticks([0, 300])
    ax.set_yticks([0, 125, 250])
    # plt.xlabel('Time', fontsize=16)
    # plt.ylabel('Swarm length', fontsize=18)

    plt.tight_layout()
    fig.savefig(folder_path + '/0115-swarm-distance'+name+'.pdf')
    print(folder_path + '/swarm-distance'+name+'.pdf')
    ax.clear()
    plt.clf()
    plt.close()
    
# def copy_trajectory_files(fig_path):
#     folder_list = fig_path.rsplit('/',5)
#     destination_init_path = folder_list[0] + '/fig/' + folder_list[1] + '-' + folder_list[2] + '-' + folder_list[3] + '-' + folder_list[5] + '-init.pdf'
#     destination_trace_path = folder_list[0] + '/fig/' + folder_list[1] + '-' + folder_list[2] + '-' + folder_list[3] + '-' + folder_list[5] + '-trajectory.pdf'
#     source_init_path = fig_path + '-gen.pdf'
#     source_trace_path = fig_path.rsplit('/',2)[0] +'/gif/' + fig_path.rsplit('/',2)[2] + '-gen.pdf'
#     if not os.path.exists(folder_list[0] + '/fig/'):
#         os.makedirs(folder_list[0] + '/fig/')
#     shutil.copy(source_init_path, destination_init_path)
#     shutil.copy(source_trace_path, destination_trace_path)


def plot_program(directory_path, shepherd_num):
    param_path = str(directory_path) + str('setting.json')
    print(param_path)
    param = get_param(param_path)

    shepherds = range(param["shepherd_number"][0], param["shepherd_number"][1] + 1)
    sheeps = range(param["sheep_number"][0], param["sheep_number"][1] + 1)
    trials = range(param["trial_number"])

    # shepherd_num = shepherds[0]
    sheep_num = sheeps[0]
    trial_num = trials[0]
    file_path = directory_path + 'data/' + '{}sh{}tr{}.csv'.format(str(shepherd_num), str(sheep_num), str(trial_num))    
    with open(file_path) as f:
        reader = csv.reader(f, delimiter=',')
        line_count = count_line(file_path)
        # For trace
        sheeps_pos_list = []
        sheeps_vel_list = []
        shepherds_pos_list = []
        shepherds_vel_list = []
        shepherds_targets_pos = []
        index = 0
        # row_num = 0
        for row in reader:
            if index >= line_count-1: # until the second last line
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
            # Shepherd may not have a target if it does not see anything
            for i in range(length, len(row)):
                if judge_str_not_none(row[i]):
                    value = str_to_attribute_nparray(row[i])
                    shepherds_targets_pos_row.append(value)
                else: 
                    shepherds_targets_pos_row.append(None)

            sheeps_vel_list.append(sheeps_vel_row)
            sheeps_pos_list.append(sheeps_pos_row)
            shepherds_vel_list.append(shepherds_vel_row)
            shepherds_pos_list.append(shepherds_pos_row)
            shepherds_targets_pos.append(shepherds_targets_pos_row)
            index+=1

        # After finishing the loop
        fig_path = directory_path + 'graph/{}sh{}tr{}'.format(str(shepherd_num), str(sheep_num), str(trial_num))
        # if not os.path.exists(fig_path):
        #     os.makedirs(fig_path)
        
        # calculate_sheep_distance_data(fig_path, sheeps_pos_list)
        plot_distance_to_goal_graph(fig_path, param, sheeps_pos_list, shepherds_pos_list)

        # copy_trajectory_files(fig_path)
        
if __name__ == '__main__':
    sns.set(style='white')

    # matplotlib.rcParams['pdf.fonttype'] = 42
    # matplotlib.rcParams['ps.fonttype'] = 42
    
    home_path = '/home/li-aiyi/program/shepherding-public/shepherding-log/log/'
    
    # init
    # folder_path = 'config/2023-11-02_shepherd/init/model1' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # folder_path = 'config/2023-11-02_shepherd/init/model2' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # folder_path = 'config/2023-11-02_shepherd/init/model3' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # for path in path_list:
    #     plot_program(path)
        

    
    # """ 1 """
    path_list = []
    folder_path = 'config/2023-11-02_shepherd/1swarm/model1' + '/'
    base = home_path + folder_path
    path_list.extend(findFolder(base))
    
    # folder_path = 'config/2023-11-02_shepherd/1swarm/model2' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # folder_path = 'config/2023-11-02_shepherd/1swarm/model3' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    # for path in path_list:
    #     plot_program(path, 3)

    # """ 2 """
    # path_list = []
    # folder_path = 'config/2023-11-02_shepherd/2swarm/model1' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # # folder_path = 'config/2023-11-02_shepherd/2swarm/model2' + '/'
    # # base = home_path + folder_path
    # # path_list.extend(findFolder(base))
    
    # # folder_path = 'config/2023-11-02_shepherd/2swarm/model3' + '/'
    # # base = home_path + folder_path
    # # path_list.extend(findFolder(base))

    # for path in path_list:
    #     plot_program(path, 5)
        
    """ 3 """
    path_list = []
    folder_path = 'config/2023-11-02_shepherd/3swarm/model1' + '/'
    base = home_path + folder_path
    path_list.extend(findFolder(base))
    
    # folder_path = 'config/2023-11-02_shepherd/3swarm/model2' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    # folder_path = 'config/2023-11-02_shepherd/3swarm/model3' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    for path in path_list:
        plot_program(path, 7)

    """ Plot swarm length """
    # path_list = []
    # folder_path = 'config/2023-11-02_shepherd/init/model1/1' + '/'
    # path_list.append(home_path + folder_path)

    # folder_path = 'config/2023-11-02_shepherd/init/model2/1' + '/'
    # path_list.append(home_path + folder_path)

    # folder_path = 'config/2023-11-02_shepherd/init/model3/1' + '/'
    # path_list.append(home_path + folder_path)

    # plot_init_length_list(path_list,'1')
    
    
    # path_list = []
    # folder_path = 'config/2023-11-02_shepherd/init/model1/2' + '/'
    # path_list.append(home_path + folder_path)

    # folder_path = 'config/2023-11-02_shepherd/init/model2/2' + '/'
    # path_list.append(home_path + folder_path)

    # folder_path = 'config/2023-11-02_shepherd/init/model3/2' + '/'
    # path_list.append(home_path + folder_path)

    # plot_init_length_list(path_list,'2')
    
    
    # path_list = []
    # folder_path = 'config/2023-11-02_shepherd/init/model1/3' + '/'
    # path_list.append(home_path + folder_path)

    # folder_path = 'config/2023-11-02_shepherd/init/model2/3' + '/'
    # path_list.append(home_path + folder_path)

    # folder_path = 'config/2023-11-02_shepherd/init/model3/3' + '/'
    # path_list.append(home_path + folder_path)

    # plot_init_length_list(path_list,'1')
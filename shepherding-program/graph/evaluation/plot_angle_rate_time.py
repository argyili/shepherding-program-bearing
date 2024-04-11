import numpy as np
import math
import pandas as pd
import csv
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import shutil

def findFolder(base):
    path_list = os.listdir(base)
    path_list.sort()  
    for f in path_list:
        path = os.path.join(base, f)
        if not os.path.isdir(path): # if not a folder, ignore it
            continue
        yield base + f + '/'
        
def complement_dict(json_dict):
    with open('./config/default.json', 'r') as f:
        default_dict = json.load(f)

    for k in default_dict.keys():
        if k not in json_dict:
            json_dict[k] = default_dict[k]

    return json_dict

def load(json_path, complement=True):
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

def get_param(param_file_path):
    '''
    Get prameters in dict
    '''
    param = load(param_file_path)
    return param

def read_file(path):
    list = []
    with open(path, mode='r') as f:
        reader = csv.reader(f)
        # Start from line 1, line 1 not existed
        for row in reader:
            list.append(row)
    f.close()
    return list

def get_full_list(directory_path, shepherd_nums):
    list = []
    # Shepherd number starts from 1
    for i in shepherd_nums:
        file_path = directory_path + '/data/' + str(i) + '.csv'
        list.append(read_file(file_path))
    return list

def copy_plot_files(folder_path):
    folder_list = folder_path.rsplit('/',4)
    source_path = folder_path + 'plot_angle.pdf'
    destination_path = folder_list[0] + '/fig/' + folder_list[1] + '-' + folder_list[2] + '-' + folder_list[3] + '-plot_angle.pdf'
    if not os.path.exists(folder_list[0] + '/fig/'):
        os.makedirs(folder_list[0] + '/fig/')
    shutil.copy(source_path, destination_path)
    
def plot_angle(path_list,angle_list):
    dfs = []
    for folder_path in path_list:
        file_path = folder_path + 'result.csv'
        df = pd.read_csv(file_path)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    df.columns = ['shepherd','sheep','method','rate','step','var_step','distance','var_dis']
    print(angle_list)
    df['angle'] = angle_list
    
    fig, ax1 = plt.subplots(figsize=(8,6))
    
    # x = range(-0.1,1.1) # angle range
    ax1.plot(df['angle'], df['rate'], marker='o', color='tab:blue', label='rate')
    ax1.set_xlabel('Angle precision', fontsize=12)
    ax1.set_ylabel('Success rate', color='tab:blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_yticks([0,1], fontsize=16)
    ax1.set_ylim([-0.05,1.05])

    ax2 = ax1.twinx()
    ax2.plot(df['angle'], df['step'], marker='o', color='tab:orange', label='time')
    ax2.set_ylabel('Time', color='tab:orange', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    # ax2.set_yticks([0,700], fontsize=16)
    ax2.set_yticks([0,1500,3000], fontsize=16)
    ax2.set_ylim([-150,3150])
    # ax2.set_yticks([0,1500], fontsize=16)
    
    # ax1.set_xticks([0,0.2,0.4,0.6,0.8,1.0], fontsize=16)
    # ax1.set_xticks([0,0.5,1.0,1.5,2.0], fontsize=16)
    ax1.set_xticks([0,0.5,1.0,1.5,2.0,2.5,3.0], fontsize=16)
    
    plt.tight_layout()
    fig.savefig(path_list[0] + 'plot_angle.pdf')

if __name__ == '__main__':
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    
    home_path = '/home/li-aiyi/program/shepherding-public/shepherding-log/log/'

    folder_path = 'config/2023-11-11_angle-3/'
    swarm_list = ['1swarm','2swarm','3swarm']
    prefix = '-precision'
    angle_list = ['0','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
    angle_true_list = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0]
    model_list = ['model1','model2','model3']
    type_list = ['behind','goal','surround']
    for swarm in swarm_list:
        for model in model_list: # model loop first           
            for type in type_list:
                path_list = []
                for angle in angle_list:            
                    base = home_path + folder_path + swarm + '/' + swarm + prefix + angle +'/'+ model +'/' + type + '/'
                    print(base)
                    path_list.append(base)
                
                plot_angle(path_list,angle_true_list)
                copy_plot_files(path_list[0])            
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
    folder_list = folder_path.rsplit('/',5)
    source_path = folder_path + '/boxplot_angle.svg'
    destination_path = folder_list[0] + '/fig/' + folder_list[2] + '-' + folder_list[3] + '-' + folder_list[4] + '-boxplot_angle.svg'
    if not os.path.exists(folder_list[0] + '/fig/'):
        os.makedirs(folder_list[0] + '/fig/')
    shutil.copy(source_path, destination_path)
    
def plot_angle(path_list, angle_list, angle_true_list, num):
    dfs = []
    for path in path_list:
        file_path = path + '/data/' + str(num) + '_all.csv'
        df = pd.read_csv(file_path)
        dfs.append(df['step'])

    fig, ax = plt.subplots(figsize=(8,6))

    ax.boxplot(dfs)
    ax.set_xticks(angle_list, angle_true_list, fontsize=16)
    ax.set_xlim([-0.5,30.5])

    ax.set_yticks([0,1500,3000], [0,1500,3000], fontsize=16)
    ax.set_ylim([-150,3150])
    
    plt.tight_layout()
    fig.savefig(path_list[0] + 'boxplot_angle.svg')

if __name__ == '__main__':
    # matplotlib.rcParams['svg.fonttype'] = 42
    # matplotlib.rcParams['ps.fonttype'] = 42
    
    home_path = '/home/li-aiyi/program/shepherding-public/shepherding-log/log/'

    folder_path = 'config/2023-11-11_angle-3/'
    swarm_list = ['1swarm','2swarm','3swarm']
    # swarm_list = ['3swarm']
    prefix = '-precision'
    angle_list = ['0','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
    angle_num_list = [0,5,10,15,20,25,30]
    angle_true_list = [0,0.5,1.0,1.5,2.0,2.5,3.0]
    model_list = ['model1','model2','model3']
    type_list = ['behind','goal','surround']
    numbers = [3,5,7]
    i = 0
    for swarm in swarm_list:
        num = numbers[i]
        i += 1
        for model in model_list: # model loop first           
            for type in type_list:
                path_list = []
                for angle in angle_list:            
                    base = home_path + folder_path + swarm + '/' + swarm + prefix + angle +'/'+ model +'/' + type + '/'
                    print(base)
                    path_list.append(base)
                
                plot_angle(path_list,angle_num_list,angle_true_list, num)
                copy_plot_files(path_list[0])            
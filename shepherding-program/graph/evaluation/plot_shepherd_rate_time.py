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
    source_path = folder_path + 'plot.pdf'
    destination_path = folder_list[0] + '/fig/' + folder_list[1] + '-' + folder_list[2] + '-' + folder_list[3] + '-plot.pdf'
    if not os.path.exists(folder_list[0] + '/fig/'):
        os.makedirs(folder_list[0] + '/fig/')
    shutil.copy(source_path, destination_path)
    
def plot_program(folder_path):
    file_path = folder_path + 'result.csv'
    df = pd.read_csv(file_path)
    df.columns = ['shepherd','sheep','method','rate','step','var_step','distance','var_dis']
    
    fig, ax1 = plt.subplots(figsize=(8,6))
    x = np.arange(1,len(df['shepherd'])+1)
    ax1.plot(df['shepherd'], df['rate'], marker='o', color='tab:blue', label='rate')
    ax1.set_xlabel('Shepherd number', fontsize=12)
    ax1.set_ylabel('Success rate', color='tab:blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_yticks([0,1], fontsize=16)
    ax1.set_ylim([-0.05,1.05])

    ax2 = ax1.twinx()
    ax2.plot(df['shepherd'], df['step'], marker='o', color='tab:orange', label='time')
    ax2.set_ylabel('Time', color='tab:orange', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    # ax2.set_yticks([0,700], fontsize=16)
    ax2.set_yticks([0,1500,3000], fontsize=16)
    # ax2.set_yticks([0,1500], fontsize=16)
    ax2.set_ylim([-150,3150])
    
    ax1.set_xticks(x)
    # ax1.set_xticks([1,2,3,4,5], fontsize=16)
    ax1.set_xticks([2,4,6,8,10], fontsize=16)
    
    plt.tight_layout()
    fig.savefig(folder_path + 'plot.pdf')

    print(folder_path)

if __name__ == '__main__':
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    
    path_list = []
    home_path = '/home/li-aiyi/program/shepherding-public/shepherding-log/log/'
    
    """ 1 """
    # folder_path = 'config/2023-11-02_shepherd/1swarm/model1' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    # folder_path = 'config/2023-11-02_shepherd/1swarm/model2' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # folder_path = 'config/2023-11-02_shepherd/1swarm/model3' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # """ 2 """
    folder_path = 'config/2023-11-02_shepherd/2swarm/model1' + '/'
    base = home_path + folder_path
    path_list.extend(findFolder(base))

    # folder_path = 'config/2023-11-02_shepherd/2swarm/model2' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    # folder_path = 'config/2023-11-02_shepherd/2swarm/model3' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))

    # """ 3 """
    # folder_path = 'config/2023-11-02_shepherd/3swarm/model1' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    # folder_path = 'config/2023-11-02_shepherd/3swarm/model2' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    # folder_path = 'config/2023-11-02_shepherd/3swarm/model3' + '/'
    # base = home_path + folder_path
    # path_list.extend(findFolder(base))
    
    for path in path_list:
        plot_program(path)
        
    for path in path_list:
        copy_plot_files(path)
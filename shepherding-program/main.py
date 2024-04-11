from abc import abstractmethod
import os
import datetime
import argparse 
from multiprocessing import Pool
import shutil # danger

import shepherding as ss
from shepherding.util import analyze 
from shepherding.util import config
from shepherding.util import disk_info

import matplotlib
    
''' Multiprocessing for running batch programs '''
def multiprocess(param, directory_path, is_gif):
    shepherds = range(param['shepherd_number'][0], param['shepherd_number'][1] + 1)
    sheeps = range(param['sheep_number'][0], param['sheep_number'][1] + 1)
    trials = range(param['trial_number'])

    ssTrail = ss.trial.Trial(param, directory_path) 
    values_trial = [(shepherd_num, sheep_num, trial) for sheep_num in sheeps for shepherd_num in shepherds for trial in trials]
    pool = Pool(processes=param['process_number'])
    pool.starmap(ssTrail.trial_loop_csv, values_trial)

    values_csv = [(directory_path, shepherd_num, sheep_num, trials) for shepherd_num in shepherds for sheep_num in sheeps]
    pool.starmap(analyze.full_csv, values_csv)

    # Generate kinds of graphs for analysis
    # Default from 0 or 1, suitable to shepherds, sheeps and trials
    gen_graph(directory_path, shepherds, sheeps, trials, param, is_gif)

''' Generate graph for visualizing after results '''
def gen_graph(directory_path, shepherd_nums, sheep_nums, trial_nums, param, is_gif=False):
    analyze.write_csv(directory_path, directory_path+'/result.csv', shepherd_nums)
    
    if is_gif:
        values = [(directory_path, shepherd_num, sheep_num, trial, param, 4000) for shepherd_num in shepherd_nums for sheep_num in sheep_nums for trial in trial_nums]
        pool = Pool(processes=param['process_number'])
        pool.starmap(analyze.gen_all_trace, values)
        pool.starmap(analyze.gen_gifs, values)

def make_dir(folder_path):
    '''
    Create directory by its name 
    Format: yyyy_MMdd_HHMMSS
    ''' 
    # Name specially    
    if os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
    graph_path = folder_path + '/graph'
    data_path = folder_path + '/data'
    gif_path = folder_path + '/gif'
    png_path = folder_path + '/png'

    os.makedirs(graph_path) 
    os.makedirs(data_path)
    os.makedirs(gif_path)
    os.makedirs(png_path)
    
    return os.path.abspath(folder_path)

def get_param(param_file_path):
    '''
    Get parameters as a dict
    '''
    param = config.load(param_file_path)
    return param

def arg_parse():
    '''
    Parse arguments
    '''
    parser = argparse.ArgumentParser(description='Shepherding Program')
    parser.add_argument('-p', '--param_file_path', default='./config/default.json', help='parameter file path')
    parser.add_argument('-g', '--gif', action='store_true', help='generate gif and trace graph')

    now = datetime.datetime.now()
    return parser.parse_args()

if __name__ == '__main__':
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    folder_path = '/home/li-aiyi/program/shepherding-public/shepherding-log/log/' # Path should be changed to each own environment
    args = arg_parse()
    param = get_param(args.param_file_path)
    if args.param_file_path.endswith('.json'):
        args.param_file_path = args.param_file_path[:-5]
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    path = args.param_file_path
    
    folder_path = folder_path + path
    # folder_path = folder_path + path.rsplit('/', 1)[0] + '/' + path.rsplit('/', 1)[1] + '_' + current_time
    
    # In case overwrite the result
    if os.path.isfile(folder_path + '/result.csv'):
        print(folder_path + '/result.csv')
    else:        
        print(folder_path)
        dir_path = make_dir(folder_path)                
        config.write_reshaped(dir_path + '/setting.json', param)
        multiprocess(param, dir_path, args.gif)
    
        # Warn disk usage
        disk_info.warn_directory_size(dir_path)
        disk_info.warn_disk_usage(limit_percentage=80)
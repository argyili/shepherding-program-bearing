import os
from multiprocessing import Pool
import time

def find_file(base):
    path_list = os.listdir(base)
    path_list.sort()  
    for f in path_list:
        path = os.path.join(base, f)
        if os.path.isdir(path):
            continue
        yield base, f 

# def find_file_model(base):
#     model_list = ['model1/','model2/','model3/']
#     for model in model_list:
#         base_model = os.path.join(base, model)
#         path_list = os.listdir(base_model)
#         path_list.sort()  
#         for f in path_list:
#             path = os.path.join(base_model, f)
#             print(path)
#             if os.path.isdir(path):
#                 continue
#             yield base_model, f 

def program(tuple):
    base = tuple[0]
    f =tuple[1]
    f_nosuffix = f
    if f.endswith('.json'):
        f_nosuffix = f[:-5]

    folder = '/home/li-aiyi/program/shepherding/shepherding-log/log/'

    # if file name repeated, stop running
    if os.path.isfile(folder + base + '/' + f_nosuffix + '/result.csv'):
        print(base + f_nosuffix + '/result.csv')
        return

    str = "python3 main.py -p " + "\"" + base + '/' + f + "\"" + " -g"

    with open("log/log-degree.txt", "a") as f:
        f.writelines('Start: ' + str + '\n')
        f.close()
    print('Start: ' + str)

    os.system(str)
    
    with open("log/log-degree.txt", "a") as f:
        f.writelines('End: ' + str + '\n')
        f.close()
    print('End: ' + str)

def main():
    list = []

    folder_path = 'config/2024-02-01_shepherd_no-comm'
    swarm_list = ['1swarm','2swarm','3swarm']
    model_list = ['model1','model2','model3']
    for swarm in swarm_list:
        for model in model_list:
            base = folder_path + '/' + swarm + '/' + model
            list.extend(find_file(base))
    
    p = Pool(10) 
    # We sould let pool go sequencely alphabatically / arabic numerically
    p.map(program, list, chunksize=1)

if __name__ == '__main__':
    main()

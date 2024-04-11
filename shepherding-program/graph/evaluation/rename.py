import os

def findFolder(base):
    path_list = os.listdir(base)
    path_list.sort()  
    for f in path_list:
        path = os.path.join(base, f)
        if not os.path.isdir(path): # if not a folder, ignore it
            continue
        yield base + f + '/'

if __name__ == '__main__':
    path_list = []
    home_path = '/home/li-aiyi/program/shepherding-public/shepherding-log/log/'

    folder_path = 'config/2023-10-12_placement/'
    swarm_list = ['1swarm','2swarm','3swarm']
    prefix = '-precision'
    subfolder_list = ['0/','01/','02/','03/','04/','05/','06/','07/','08/','09/','10/']
    model_list = ['model1/','model2/','model3/']
    # type_list = ['behind','goal','surround']
    for swarm in swarm_list:
        for model in model_list: # model loop first           
            for subfolder in subfolder_list:            
            # for type in type_list:
                base = home_path + folder_path + swarm + prefix + subfolder + model
                path_list.extend(findFolder(base))

    for path in path_list: 
        path_rename = path.rsplit('_',2)[0] + '/' # split '_' from the reverse direction and intro three parts and take the first part (longest part)
        os.rename(path, path_rename)

from shepherding.method.degree.degree import Degree_Shepherd

''' Select shepherd method'''
def select_shepherd_method(name, init_param):
    if name == 'degree':
        return Degree_Shepherd(init_param)
    else:
        raise Exception('Invalid shepherd method selected')
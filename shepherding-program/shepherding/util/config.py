import json
import re

def load(json_path):
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
    
    return json_dict
    
def write_reshaped(json_path, dict):
    '''
    Output formatted data in dict format
    '''
    with open(json_path, 'w') as f:
        dump_data = json.dumps(dict, indent=4)
        # Remove line breaks in areas enclosed by '[' and ']'.
        re_dump_data = re.sub('\[(.*?)\]',dashrepl, dump_data, flags=re.DOTALL)

        f.write(re_dump_data)

def dashrepl(matchobj):
    return matchobj.group(0).replace("\n", "").replace(" ", "")
import configparser
import os
from pathlib import Path

filepath = Path('/fusion/projects/boundary/guterlj/hermes/hermes-3-petsc/build/examples/1D-te-ti/BOUT_.inp')
filepath2 = Path('/fusion/projects/boundary/guterlj/hermes/hermes-3-petsc/build/examples/1D-te-ti/BOUT.inp')


def parse_bout_configfile(filepath):
    fp = Path(filepath)
    with fp.open("r") as config_file:
        s = f"[global]\n{config_file.read()}"
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option
    config.read_string(s)
    return config

def write_bout_configfile(fp, config):
    filepath = Path(fp)
    assert not os.path.isfile(filepath), f"the file {filepath} already exists..."
    with filepath.open("w") as configfile:
            config.write(configfile)
    with filepath.open('r') as fin:
        data = fin.read().splitlines(True)
    with filepath.open('w') as fout:
        fout.writelines(data[1:])

def modify_bout_parameters(config, params):

# the destination configuration
    new_config = configparser.ConfigParser()
    new_config.optionxform = lambda option: option
    new_config.read_dict(config)
    for (k,v) in params.items():
        group = k.split(".")
        set_value_param(new_config, group, v)
    return new_config
        
def set_value_param(config, group, v):
    if len(group) > 1:
        attr = group[0]
        group = group[1:]
        set_value_param(config[attr], group, str(v))
    else:
        attr = group[0]
        config[attr] = v 
    

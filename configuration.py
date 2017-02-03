import os
import yaml
from flask import request
from shutil import copyfile
from jsonschema import validate

def open_config(conf, path, path_t):
    try:
        request.form['validate']
        return request.form['config']
    except:
        if os.path.exists(path):
            copyfile(path, path_t)
            file = open(path_t, 'r')
            conf = file.read()
            file.close()
            os.remove(path_t)
        return conf

def validate_yaml(loads):
    schema = """
    required:
       - users
       - coreos
       - hostname
       - write_files
    """
    try:
        validate(yaml.load(loads), yaml.load(schema))
        yaml.safe_load(loads)
        return True
    except:
        return False

def write_config(conf, path, path_t, path_old):
    if request.__dict__['environ']['REQUEST_METHOD'] == 'POST':
        try:
            return validate_yaml(request.form['config'])
        except:
            if os.path.exists(path):
                if os.path.exists(path_old):
                  os.remove(path_old)
                copyfile(path, path_old)
            try:
                if validate_yaml(request.form['config']):
                    file = open(path_t, 'w+')
                    file.writelines(request.form['config'])
                    file.close()
                    copyfile(path_t, path)
                    os.remove(path_t)
                else:
                    return validate_yaml(request.form['config'])
            except:
                if os.path.exists(path):
                    if os.path.exists(path_old):
                      os.remove(path)
                    copyfile(path_old, path)
                    os.remove(path_old)
    return True

def get_conf(path=None):
    x = []
    conf = []
    try:
        for i in os.listdir(path):
            try:
                if i.split(sep='.')[1] == "conf":
                    conf.append(os.path.join(path, i))
            except:
                pass
    except FileNotFoundError:
        return False
    for i in conf:
        file = open(i, 'r')
        for j in file.readlines():
            x.append(j)
        x.append('[End]')
    x.append('[End]')
    return list(map(lambda x: x.replace('\n', ''), x))

def get_section(section, path='/data/config'):
    r = []
    x = False
    if not get_conf(path=path):
        return False
    for i in range(0, len(get_conf(path=path))):
        try:
            if get_conf(path=path)[i][0] == '[':
                x = False
        except IndexError:
            pass
        finally:
            if x:
                r.append(get_conf(path=path)[i])
            try:
                if get_conf(path=path)[i] == section:
                    x = True
            except IndexError:
                pass
    return r

if __name__ == "__main__":
    print(get_section('[Check HTTP]'))
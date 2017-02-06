import os
import yaml
from jsonschema import validate


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

def get_val(section):
    x = get_section(section)
    r = []
    d = {}
    for i in range(0, len(x)+1):
        if i == len(x)+1:
            r.append(d)
            break
        try:
            if x[i][0:2] == '{{':
                if d.get('name'):
                    r.append(d)
                    d = {}
                d['name'] = x[i].replace('{{', '').replace('}}', '')
                continue
            d[x[i].split(sep='=')[0]] = x[i].split(sep='=')[1]
        except IndexError:
            pass
    return r

if __name__ == "__main__":
    print('{{ddd'[0:2])
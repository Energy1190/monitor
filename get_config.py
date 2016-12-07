import os
import sys

def get_conf():
    x = []
    path = None
    conf = []
    try:
        for i in sys.argv:
            if "config_path=" in i:
                path = i.split(sep='=')[1]
    except:
        if not path:
            path = "/data/config/"

    for i in os.listdir(path):
        try:
            if i.split(sep='.')[1] == "conf":
                conf.append(os.path.join(path, i))
        except:
            pass
    for i in conf:
        file = open(i, 'r')
        for j in file.readlines():
            x.append(j)
        x.append('[End]')
    x.append('[End]')
    return x

def get_section(section):
    r = []
    x = False
    for i in range(0, len(get_conf())):
        if get_conf()[i][0] == '[':
            x = False
        if x:
            r.append(i)
        if get_conf()[i] == section:
            x = True
    return r

if __name__ == "__main__":
    print(os.listdir('/Users'))
import os
import sys

def get_conf(path=None):
    x = []
    conf = []
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
    return list(map(lambda x: x.replace('\n', ''), x))

def get_section(section, path='/data/config'):
    r = []
    x = False
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
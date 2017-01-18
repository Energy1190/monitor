import time
from db import db_get, db_find, db_update, db_set, db_del, db_del_all

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def return_nub(x):
    return int(''.join([i for i in x if isfloat(i)]))

class Base():
    def set_dict(self):
        self.dict = {i: self.__dict__[i] for i in self.__dict__ if i != 'dict' and i != 'message'}

class Comp(Base):
    def __init__(self, trg):
        self.computername = trg['Userinfo']['Computername']
        self.system = trg['Systeminfo']
        self.hard = trg['Harddriveinfo']
        self.disk = trg['Diskinfo']
        self.network = trg['Networkinfo']
        self.groups = trg['Groupsinfo']
        self.errors = trg['Errorinfo']
        self.programm = trg['Programsinfo']
        self.service = trg['Serviceinfo']
        self.task = trg['Tasksinfo']
        self.psversion = trg['Version']
        self.dict = self.set_dict()

class User(Base):
    def __init__(self, trg):
        self.username = trg['Userinfo']['Username']
        self.domain = trg['Userinfo']['Domainname']
        self.computername = trg['Userinfo']['Computername']
        self.time = time.strftime('%d.%m.%Y %H:%M:%S',  time.gmtime(return_nub(trg['Timeinfo'])/1000.))
        self.copmslist = [{self.computername: self.time}]
        self.dict = self.set_dict()
        try:
            self.grouppolicy = trg['GroupPolicyinfo']
        except:
            pass

class Route(Base):
    def __init__(self, trg):
        self.time = eval(trg['time'])
        self.message = trg['message']
        self.dict = self.set_dict()

def edit_json():
    try:
        trg = db_get('New', target=['clients', 'json'], fild='Status')
    except:
        trg = False
    if trg:
        if int(trg['Version']) > 2:
            trgt = Comp(trg)
            db_trg = db_get(trg['Userinfo']['Computername'], target=['clients', 'comps'], fild='computername')
            if not db_trg:
                db_set(trgt.dict, target=['clients', 'comps'])
                pass
            else:
                for i in list(db_trg):
                    try:
                        if i != '_id' and db_trg[i] != trgt.dict[i]:
                            db_update(trgt.dict, target=['clients', 'comps'], id=str(db_trg['_id']))
                            break
                    except KeyError:
                        pass
        usr_trg = db_get(trg['Userinfo']['Username'], target=['clients', 'users'], fild='username')
        if not usr_trg:
            db_set(User(trg).dict, target=['clients', 'users'])
        else:
            trgt = User(trg)
            trgt.copmslist = usr_trg['copmslist'].append({trgt.computername: trgt.time})
            db_update(trgt.dict, target=['clients', 'users'], id=str(usr_trg['_id']))
        db_update({'Status': 'Old'}, target=['clients', 'json'], id=str(trg['_id']))

def delete_old_reqests(target, status='Old'):
    try:
        if status:
            trg = db_get(status, target=target, fild='Status')
            for i in trg:
                db_del(i, target=target)
        else:
            db_del_all(target=target)
    except:
        pass

def check_base(target):
    y = []
    x = db_find(target=target)
    if target[1] == 'comps':
        name = 'computername'
    elif target[1] == 'users':
        name = 'username'
    else:
        return False
    for i in x:
        for j in i:
            if j == name:
                if i[j]:
                    if i[j] not in y:
                        y.append(i[j])
                        break
                    else:
                        print('delete:', i)
                        db_del(i, target=target)
                else:
                    print('delete:', i)
                    db_del(i, target=target)
        if name not in i:
            db_del(i, target=target)


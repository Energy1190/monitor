import time
from db import db_get, db_find, db_update, db_set, db_del

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def return_nub(x):
    return int(''.join([i for i in x if isfloat(i)]))

class Comp():
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

class User():
    def __init__(self, trg):
        self.username = trg['Userinfo']['Username']
        self.domain = trg['Userinfo']['Domainname']
        self.computername = trg['Userinfo']['Computername']
        self.time = time.strftime('%d.%m.%Y %H:%M:%S',  time.gmtime(return_nub(trg['Timeinfo'])/1000.))
        self.copmslist = [{self.computername: self.time}]
        try:
            self.grouppolicy = trg['GroupPolicyinfo']
        except:
            pass

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
                db_set(Comp(trg).__dict__, target=['clients', 'comps'])
                pass
            else:
                for i in list(db_trg):
                    try:
                        if db_trg[i] != trgt.__dict__[i] and i != '_id':
                            db_update({i: trgt.__dict__[i]}, target=['clients', 'comps'], id=str(db_trg['_id']))
                    except KeyError:
                        pass
        usr_trg = db_get(trg['Userinfo']['Username'], target=['clients', 'users'], fild='username')
        if not usr_trg:
            db_set(User(trg).__dict__, target=['clients', 'users'])
        else:
            trgt = User(trg)
            for i in list(usr_trg):
                try:
                    if usr_trg[i] != trgt.__dict__[i] and i != 'copmslist' and i != '_id':
                        db_update({i: trgt.__dict__[i]}, target=['clients', 'users'], id=str(usr_trg['_id']))
                except KeyError:
                    pass
            tgt_list = usr_trg['copmslist'].append({trgt.computername: trgt.time})
            db_update({'copmslist': tgt_list}, target=['clients', 'users'], id=str(usr_trg['_id']))
        db_update({'Status': 'Old'}, target=['clients', 'json'], id=str(trg['_id']))

def delete_old_reqests():
    try:
        trg = db_get('Old', target=['clients', 'json'], fild='Status')
        for i in trg:
            db_del(i, target=['clients', 'json'])
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
                        db_del(i, target=target)
                else:
                    db_del(i, target=target)
        if name not in i:
            db_del(i, target=target)

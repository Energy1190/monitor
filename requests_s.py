#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

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

    def delete(self, trg, target=None):
        if target:
            db_del(trg, target=target)

    def set(self, trg, target=None):
        if target:
            db_set(trg, target=target)

class Comp(Base):
    def __init__(self, trg, target=None):
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
    def __init__(self, trg, target=None):
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
    """ Класс обрабатывающий входящие сообщения с роутера. Согласно документации
        возможны следующие переменные:

        * name - Имя сообщения.
        * id - ID сообщения.
        * prio - Приоритет сообщения.
        * event - Описание сообщения.
        * action - Действие.
        * rev - ?.
        * conntime - Время соединения.
        * rule - Используемое правило.
        * recvif - Имя принимающего интерфейса.
        * connipproto - Протокол для данного соединения.
        * conn - Статус соединения.
        * connrecvif - Имя интерфейса отправителя.
        * conndestif - Имя интерфейса назнаяения.
        * connsrcip - IP-адрес отправителя.
        * connsrcport - Порт отправителя.
        * conndestip - IP-адрес назначения.
        * conndestport - Порт назначения.
        * origsent - Число байт, отправленных инициатором.
        * termsent - Число байт, отправленных инициатором.

        Для подсчета трафика необходимы только логи уровня Info.
        Предпологаемое место расположение в базе: 'route' - 'info'.
    """
    def __init__(self, trg, target=None):
        if trg:
            self.status = True
            self.time = eval(trg['time'])
            self.message = trg['message']
            self.level = lambda x: target[1] if len(target) > 1 else target[0](target)
            self.dict = self.set_dict()
            self.dict['level'] = self.level
            self.dict['time'] = self.time
        else:
            self.status = False

    def set_dict(self):
        if self.status:
            x = self.message.split(sep=' ')
            self.name = x[0][:-1]
            self.dict['name'] = self.name
            return {i.split(sep='=')[0]: i.split(sep='=')[0] for i in x}
        else:
            return False

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
                            trgt.computername = db_trg['computername']
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
            trgt.username = usr_trg['username']
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

def processing_incoming(target, out_target):
    t = db_get(None, target=target, fild=None)
    print(t)
    x = Route(t, target=target)
    if x.set_dict():
        x.set(x.dict, target=out_target)
        x.delete(t,target=target)
        return True
    else:
        return False

if __name__ == '__main__':
    print(help(Route))
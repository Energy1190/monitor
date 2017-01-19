#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import time
import datetime
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
    def __init__(self, trg, target=None):
        self.old = []
        self.dict = {}
        self.dst = target

    def set_dict(self):
        self.dict = {i: self.__dict__[i] for i in self.__dict__ if i != 'dict' and i != 'message' and i != 'dst'}

    def delete(self, trg, target=None):
        if target:
            db_del(trg, target=target)

    def set(self, trg, target=None):
        if target:
            db_set(trg, target=target)
        else:
            db_set(trg, target=self.dst)

    def update(self, srctrg=None, dsttrg=None, target=None):
        if target and dsttrg:
            if srctrg:
                db_update(srctrg, target=target, fild=dsttrg)
            else:
                db_update(self.dict, target=target, fild=dsttrg)
        elif dsttrg:
            if srctrg:
                db_update(srctrg, target=self.dst, fild=dsttrg)
            else:
                db_update(self.dict, target=self.dst, fild=dsttrg)

    def check_dict(self, target_dict):
        for i in self.dict:
            if i != '_id' and i != 'old' and i in target_dict:
                if self.dict[i] != target_dict[i]:
                    self.old.append({i: target_dict[i], 'time': datetime.datetime.now()})

    def get_dsttrg(self, src, fild):
        x = db_get(src, target=self.dst, fild=fild)
        if x:
            return x
        else:
            return False

class Comp(Base):
    def __init__(self, trg, target=None):
        Base.__init__(self, trg, target=target)
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
        self.old = []
        self.dict = self.set_dict()

class User(Base):
    def __init__(self, trg, target=None):
        Base.__init__(self, trg, target=target)
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

    def check_dict(self, target_dict):
        Comp.check_dict(self, target_dict)
        self.copmslist.extend(target_dict['copmslist'])

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
        Base.__init__(self, trg, target=target)
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

def get_database_incoming(target, status=None):
    try:
        if status:
            return db_get(status, target=target, fild='Status')
        else:
            return db_get(None, target=target, fild=None)
    except:
        print('Something wrong')
        return False


def processing_incoming_json(target, out_target_users, out_target_comps):
    t = get_database_incoming(target, status='New')
    if t:
        if int(t['Version']) > 2:
            x = Comp(t, target=out_target_comps)
            y = x.get_dsttrg(t['Userinfo']['Computername'], 'computername')
            if y:
                x.check_dict(y)
                x.update(dsttrg=y)
            else:
                x.set()
        x = User(t, target=out_target_users)
        y = x.get_dsttrg(t['Userinfo']['Username'], 'username')
        if y:
            x.check_dict(y)
            x.update(dsttrg=y)
        else:
            x.set()

def processing_incoming_route(target, out_target):
    t = get_database_incoming(target, status=None)
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
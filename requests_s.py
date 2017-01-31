#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import os
import time
import base64
import datetime
from Crypto.Cipher import AES
from Crypto import Random
from db import db_get, db_find, db_update, db_set, db_del, db_del_all

error_c = 0

def rec_to_str(x):
    if type(x) == list:
        for i in x:
            try:
                str(i, 'utf-8')
            except TypeError:
                rec_to_str(i)
    elif type(x) == dict:
        try:
            for i in x:
                str(x[i], 'utf-8')
        except TypeError:
            rec_to_str(x[i])
    elif type(x) == bytes:
        str(x, 'utf-8')
    else:
        error_log_write(x, err=type(x))

def error_log_write(t, err=None):
    global error_c
    error_c += 1
    if not os.path.exists('error.log'):
        file = open('error.log', 'w+')
    else:
        file = open('error.log', 'a+')
    file.write('Error № {0} \n'.format(error_c))
    file.write('Error time {0} \n'.format(datetime.datetime.now() + datetime.timedelta(hours=3)))
    if err:
        if len(t) > 500:
            t = t[0:499] + '\n...part of the text omittedpart of the text omitted...\n'
        file.write('Error string {0} \n'.format(t))
        file.write('Trace: \n')
        file.write(str(err))
    else:
        file.write('Received empty response from the base.')
    file.write('\n \n')
    file.write('--'*10)
    file.write('\n \n')
    file.close()

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
        self.dicts = {}
        self.dst = target

    def get_time_dict(self):
        if 'time' in self.__dict__:
            if type(self.time) == time.struct_time:
                self.dicts['time'] = time.strftime('%d.%m.%Y %H:%M:%S', self.time)
                self.time = datetime.datetime.fromtimestamp(time.mktime(self.time))
            else:
                self.dicts['time'] = self.time
            self.dicts['year'] = self.time.year
            self.dicts['month'] = self.time.month
            self.dicts['day'] = self.time.day
            self.dicts['hour'] = self.time.hour
            self.dicts['min'] = self.time.minute
            self.dicts['second'] = self.time.second

    def set_dict(self):
        self.dicts = {i: self.__dict__[i] for i in self.__dict__ if i != 'dicts' and i != 'message' and i != 'dst'}

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
                db_update(self.dicts, target=target, fild=dsttrg)
        elif dsttrg:
            if srctrg:
                db_update(srctrg, target=self.dst, fild=dsttrg)
            else:
                db_update(self.dicts, target=self.dst, fild=dsttrg)

    def check_dict(self, target_dict):
        for i in self.dicts:
            if i != '_id' and i != 'old' and i in target_dict:
                if self.dicts[i] != target_dict[i]:
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
        self.time = time.gmtime((return_nub(trg['Timeinfo']) + 10800000)/1000.)
        self.get_time_dict()
        self.old = []
        self.set_dict()

class Dhcp(Base):
    def __init__(self, trg, target=None):
        Base.__init__(self, trg, target=target)
        self.key = base64.b64decode(trg['Key'])
        self.body = trg['Body']
        self.text = self.decrypt(self.body)
        self.type = type(self.text)

    def set_dict(self):
        Base.set_dict(self)
        del self.dicts['key']
        del self.dicts['body']
        for i in self.dicts:
            try:
                str(self.dicts[i], 'utf-8')
            except TypeError:
                rec_to_str(self.dicts[i])

    def encrypt( self, raw ):
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return cipher.decrypt( enc[16:] )


class User(Base):
    def __init__(self, trg, target=None):
        Base.__init__(self, trg, target=target)
        self.username = str(trg['Userinfo']['Username']).lower()
        self.domain = trg['Userinfo']['Domainname']
        self.computername = trg['Userinfo']['Computername']
        self.time = time.gmtime((return_nub(trg['Timeinfo']) + 10800000)/1000.)
        self.get_time_dict()
        self.copmslist = [{self.computername: self.dicts['time']}]
        try:
            self.grouppolicy = trg['GroupPolicyinfo']
        except:
            pass
        self.set_dict()

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
        * origsent - Число байт, отправленных инициатором, исходящий трафик.
        * termsent - Число байт, отправленных инициатором, входящий трафик.

        Для подсчета трафика необходимы только логи уровня Info.
        Предпологаемое место расположение в базе: 'route' - 'info'.
    """
    def __init__(self, trg, target=None):
        if trg and 'message' in trg and 'time' in trg:
            self.status = True
            Base.__init__(self, trg, target=target)
            self.time = trg['time']
            self.message = trg['message']
            self.dicts = self.set_dict()
            self.dicts['name'] = self.name
            self.dicts['level'] = self.get_level(target)
            self.get_time_dict()
        else:
            self.status = False

    def get_level(self, x):
        if len(x) > 1:
            return x[1]
        else:
            return x[0]

    def set_dict(self):
        if self.status:
            x = self.message.split(sep=' ')
            self.name = x[0][:-1]
            x.remove(x[0])
            return {i.split(sep='=')[0]: i.split(sep='=')[1] for i in x if len(i.split(sep='=')) > 1}
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
                    if i[j].lower() not in y:
                        y.append(i[j].lower())
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
    if status:
        return db_get(status, target=target, fild='Status')
    else:
        return db_get(None, target=target, fild=None)

def processing_incoming_json(target, out_target_users, out_target_comps, dhcp_target):
    t = get_database_incoming(target, status='New')
    if t:
        if 'Version' in list(t):
            if int(t['Version']) > 2:
                x = Comp(t, target=out_target_comps)
                y = x.get_dsttrg(t['Userinfo']['Computername'], 'computername')
                if y:
                    x.check_dict(y)
                    x.update(dsttrg=y)
                else:
                    x.set(x.dicts)
            x = User(t, target=out_target_users)
            y = x.get_dsttrg(t['Userinfo']['Username'], 'username')
            if y:
                x.check_dict(y)
                x.update(dsttrg=y)
            else:
                x.set(x.dicts)
            x.delete(t, target=target)
        elif 'Key' in list(t):
            x = Dhcp(t, target=dhcp_target)
            x.set_dict()
            x.set(x.dicts)
            x.delete(t, target=target)

def processing_incoming_route(target, out_target):
    t = get_database_incoming(target, status=None)
    if t:
        x = Route(t, target=target)
        if x.set_dict():
            x.set(x.dicts, target=out_target)
            x.delete(t,target=target)
            return True
        else:
            try:
                x.delete(t,target=target)
                return False
            except Exception as err:
                error_log_write(t, err=err)

if __name__ == '__main__':
    x = User({'Userinfo' : {'Username': 'Ddd', 'Domainname' : 1, 'Computername' : 1}, 'Timeinfo': '1479477167416'})
    x.set_dict()
    print(x.dicts)
    print(eval('datetime.datetime(2017, 1, 19, 18, 0, 53)'))
    target = ['clients', 'json']
    level = lambda x: target[1] if len(target) > 1 else target[0]
    print(level(target))
    print(datetime.datetime(2017, 1, 19, 18, 0, 53).minute)

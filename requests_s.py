#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import os
import time
import json
import base64
import datetime
from Crypto.Cipher import AES
from Crypto import Random
from watch import send_mail
from db import db_get, db_find, db_update, db_set, db_del, db_del_all
from system import error_log_write, return_nub, time_now

class Base():
    """ Базовый класс для обработки входящих JSON-объектов. Включает в себя необходимые объекты:

    * old - список со значениями, которые были заменены в результате обновления записи в
    базе данных.
    * dicts - словарь, который будет по умолчанию записан в базу данных.
    * dst - коллекйия в базе данных, куда будет производиться запись, а так же откуда будут
    извлекаться значения для проверки по умолчанию.
    """
    def __init__(self, trg, target=None):
        self.old = []
        self.dicts = {}
        self.dst = target

    def encrypt( self, raw ):
        """
        Метод шифрования объектов в AES.
        :param raw:
        :return:
        """
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        """
        Метод дешифрования объектов из AES. Требует значение self.key
        :param enc:
        :return:
        """
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return cipher.decrypt( enc[16:] )

    def get_time_dict(self):
        """
        Метод для записи в словарь информации о времени. Разбитие времени на отдельные
        элементы сделано для более удобного поиска по базе данных
        :return:
        """
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
        """
        Метод для проверки идентичности словарей. Исключает
        значения _id (идентификационный номер записи в базе данных) и old
        (список со старыми значениями). В случае обнаружения различий в
        записях - записывает устаревшее значение в словарь old с указанием
        времени сделаных изменений.
        :param target_dict:
        :return:
        """
        for i in self.dicts:
            if i != '_id' and i != 'old' and i in target_dict:
                if self.dicts[i] != target_dict[i]:
                    self.old.append({i: target_dict[i], 'time': time_now})

    def get_dsttrg(self, src, fild):
        """
        Метод для получения объекта из целевой базы данных. Ищет объект по элементу
        словаря ключ(fild) - значение(src)
        :param src:
        :param fild:
        :return:
        """
        x = db_get(src, target=self.dst, fild=fild)
        if x:
            return x
        else:
            return False

class Comp(Base):
    """Класс обрабатывает информацию о компьютере на основании полученного от него
    JSON-объекта.
    """
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
    """Класс обрабатывает информацию от DHCP-сервера на основании полученного от него
    JSON-объекта. Включает в себя:

    * ip - ip-адрес выданный DHCP-сервером.
    * mac - mac-адрес компьютера получившего ip-адрес.
    * endtime - время истечения аренды ip-адреса.
    * rezervation - статус резервирования ip-адреса.
    * time - время получения данных (может быть использовано, как
    время начала подсчета трафика).

    На данный момент содержит объекты для шифрования/дешифрования входящих JSON-объектов, т.к.
    на данный момент только они шифруются. В переспективе эти объекты будут перенесены в класс Base.
    """
    def __init__(self, trg, target=None):
        Base.__init__(self, trg, target=target)
        self.key = base64.b64decode(trg['Key'])
        self.body = trg['Body']
        self.dhcpinfo = self.remove_end(self.body)
        self.timeinfo = time.gmtime((return_nub(self.dhcpinfo["Timeinfo"]) + 10800000)/1000.)
        self.dhcpinfo = self.dhcpinfo["Dhcpinfo"]
        self.dhcpinfo = self.generate_dict(self.dhcpinfo)

    def remove_end(self, x):
        for i in range(100):
            try:
                return json.loads(str(self.decrypt(x)[:-i], 'utf-8'))
            except:
                pass
        return False

    def check_time(self, x):
        if x:
            return time.gmtime((return_nub(x) + 10800000)/1000.)
        else:
            return x

    def generate_dict(self, x):
        """Метод выводит более удобочитаемый список на основании полученного JSON-объекта.
        И сортирует полученный список по IP-адресам.
        """
        return sorted([{'name': x['name'][i],
                 'ip': x['ip'][i]['IPAddressToString'],
                 'mac': x['mac'][i],
                 'endtime': self.check_time(x['timeend'][i]),
                 'time': self.timeinfo,
                 'rezervation': x['rezervation'][i]} for i in range(0, len(x['name']))], key=lambda y: y['ip'])

    def set_dict(self):
        Base.set_dict(self)
        del self.dicts['key']
        del self.dicts['body']
        del self.dicts['old']

class User(Base):
    """Класс обрабатывает информацию о пользователе на основании полученного от него
    JSON-объекта. Включает в себя:

    * username - имя пользователя, ввиду особенностей реализации необходимо переводить
    в нижний регистр, что бы избежать записей-копий.
    * domain - домен.
    * computername - имя компьютера, на который был зафиксирован последний вход.
    * time - время входа.
    * copmslist - список со всеми зафиксированными входмаи/врменными метками
    """
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

class Statistic(Base):
    def __init__(self, trg, ip, name, target=None):
        Base.__init__(self, trg, target=target)
        self.counts = 0
        self.ip = ip
        self.name = name
        self.get_user()
        self.trg = trg
        self.time = time_now
        self.data = self.summ_trafic()

    def set_dict(self):
        Base.set_dict(self)
        del self.dicts['old']
        del self.dicts['trg']

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def summ_trafic(self):
        out_t = 0
        in_t = 0
        for i in self.trg:
            self.counts += 1
            if i.get('origsent'):
                out_t += float(i['origsent'])
            if i.get('termsent'):
                in_t += float(i['termsent'])
        return {'in': self.sizeof_fmt(in_t), 'out': self.sizeof_fmt(out_t), 'in_bytes': in_t, 'out_bytes': out_t}

    def get_user(self):
        x = db_get({'computername': self.name}, target=['clients', 'users'], fild=None)
        if x:
            self.user = x['username']
        else:
            self.user = None

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

class Vals(Base):
    def __init__(self, trg, target=None):
        Base.__init__(self, trg, target=target)
        self.exeption = ['_id', 'origsent', 'termsent', 'time', 'year', 'month', 'day', 'hour', 'min', 'second']
        self.set_dict()
        if trg:
            for i in trg:
                if i not in self.exeption:
                    self.dicts[i] = trg[i]
                    x = self.get_dsttrg(src=i, fild='name')
                    if x and not x['vals'].count(str(self.dicts[i])):
                        y = x['vals']
                        y.append(str(self.dicts[i]))
                        self.update(dsttrg=x, srctrg={'name': i, 'vals': y}, target=target)
                    else:
                        y = {'name': i, 'vals': []}
                        y['vals'].append(str(self.dicts[i]))
                        self.set(y, target=target)

    def set_dict(self):
        Base.set_dict(self)
        del self.dicts['old']
        del self.dicts['exeption']

def delete_old_reqests(target, status='Old'):
    """Процедура очистки устаревших/обработанных объектов в базе данных,
    так же реализована возможность полного удаления коллекции базы данных,
    при отсутствии именованного аргумента status.
    """
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
    """Процедура проверки коллекции базы данных. На данный момент реализована
    только проверка коллекций users, copms и dhcp. Ищет и удаляет пустые, не имеющие имени,
    объекты из базы данных. Проверка осуществляется по одному ключу-значению в словаре
    назначения. Предполагается, что объект не может быть правильным без этого значения.
    Проверка осуществляется в нижнем регистре, чтобы измежать появления объектов копий.

    Функция в зависимости от переданного ей аргумента, целевой базы коллекции данных,
    определяет ключ для проверки сроваря. Если переданный аргумент не соответствует
    ожиданиям функция вернет False. Аргумент должен быть итерабельным, как минимум из
    двух элементов, в противном случае функция завершится с ошибкой.

    После определения ключа для каждого элемента в коллекции идет его проверка на
    не нулевое значение, а затем на соответствие с полученными ранее значениям (для dhcp включена
    проверка на время получения значения, будет сохраняться более новое значение), если
    проверка пройдена проверяемый объект словаря добавляется в список y и будет участвовать
    в последующих проверках, если хотя бы одна проверка не была пройдена проверяемый
    элемент удаляется из коллекции.
    """
    y = []
    x = db_find(target=target, limit=10000)
    if target[1] == 'comps':
        name = 'computername'
    elif target[1] == 'users':
        name = 'username'
    elif target[1] == 'dhcp':
        name = 'ip'
        y = {}
    else:
        return False
    for i in x:
        for j in i:
            if j == name:
                if i[j]:
                    if i[j].lower() not in y and name != 'ip':
                        y.append(i[j].lower())
                        break
                    elif name == 'ip' and str(i[j]).lower() not in list(y):
                        if y.get(str(i[j]).lower()) and i['time'] < y.get(str(i[j]).lower()):
                            print('delete:', i)
                            db_del(i, target=target)
                        else:
                            y[str(i[j]).lower()] = i['time']
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
        try:
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
                    for i in x.dicts['dhcpinfo']:
                        y = x.get_dsttrg(i['name'], 'name')
                        if y:
                            if str(y['ip']) != str(i['ip']):
                                x.update(srctrg=i, dsttrg=y)
                        else:
                            x.set(i)
                    x.delete(t, target=target)
        except Exception as err:
            error_log_write(t, err=err)
            send_mail(str(t), host='local error')
            db_del(t, target=target)

if __name__ == '__main__':
    pass
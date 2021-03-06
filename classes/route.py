import datetime
from traceback import format_exc
from classes.base_old import Base
from classes.db_mongo import Database
from system.logmodule import logger


class Dictory():
    pass

class Stat(Dictory):
    def __init__(self, *args, dicts=None):
        if dicts:
            self.trg = dicts
            self.set_level()
        else:
            self.trg = self.generate_stat(*args)
            self.set_level()

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def set_level(self):
        x = int(self.trg['data']['in_bytes']) + int(self.trg['data']['out_bytes'])
        if not x:
            self.trg['level'] = 'zero'
            self.trg['level_num'] = 0
        elif x <= 1026:
            self.trg['level'] = 'default'
            self.trg['level_num'] = 1
        elif x <= 1024000:
            self.trg['level'] = 'active'
            self.trg['level_num'] = 2
        elif x <= 1024000000:
            self.trg['level'] = 'info'
            self.trg['level_num'] = 3
        elif x <= 5120000000:
            self.trg['level'] = 'warning'
            self.trg['level_num'] = 4
        elif x > 5120000000:
            self.trg['level'] = 'danger'
            self.trg['level_num'] = 5

    def __str__(self):
        return str(self.trg)

    def __getitem__(self, item):
        return self.trg[item]

    def get(self, obj):
        return self.trg.get(obj)

    def __add__(self, other):
        try:
            if str(self.trg['ip']) == str(other['ip']):
                self.trg['counts'] = int(self.trg['counts']) + int(other['counts'])
                if other.get('name') and self.get('name') and self.trg.get('name') != other['name']:
                    self.trg['oldname'] = [{self.trg['name']: other['time']}]
                    self.trg['name'] = other['name']
                if other.get('user') and self.get('user') and self.get('user') != other['user']:
                    self.trg['olduser'] = {self.trg['user']: other['time']}
                    self.trg['user'] = other['user']
                if 'in_bytes' in list(self.trg['data']) and 'out_bytes' in list(self.trg['data']):
                    self.trg['data']['in_bytes'] = int(self.trg['data']['in_bytes']) + int(other['data'].get('in_bytes') or 0)
                    self.trg['data']['out_bytes'] = int(self.trg['data']['out_bytes']) + int(other['data'].get('out_bytes') or 0)
                    self.trg['data']['in'] = self.sizeof_fmt(self.trg['data']['in_bytes'])
                    self.trg['data']['out'] = self.sizeof_fmt(self.trg['data']['out_bytes'])
                self.set_level()
                return self.trg
        except:
            logger.error('Fail sum Statistics.')
            logger.error(str(format_exc()))

    def get_user(self, name, target):
        x = Database(dicts={'computername': name.split(sep='.')[0]}, target=target).get()
        if x:
            return x['username']
        else:
            return None

    def generate_stat(self, trg_list, ip, name, target):
        counts = 0
        out_t = 0
        in_t = 0
        for i in trg_list:
            counts += 1
            if i.get('origsent'):
                out_t += float(i['origsent'])
            if i.get('termsent'):
                in_t += float(i['termsent'])
        return {'data': {'in': self.sizeof_fmt(in_t), 'out': self.sizeof_fmt(out_t), 'in_bytes': in_t, 'out_bytes': out_t},
                'counts': counts, 'ip': ip, 'time': (datetime.datetime.now() + datetime.timedelta(hours=3)),
                'name': name, 'user': self.get_user(name, target=target)}

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




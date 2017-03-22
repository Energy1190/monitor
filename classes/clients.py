import time
import datetime
from system import return_nub
from classes.base import Base

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
        self.timeinfo = time.gmtime((return_nub(trg.get("Timeinfo")) + 10800000)/1000.)
        self.dhcpinfo = trg.get("Dhcpinfo")
        self.dhcpinfo = self.generate_dict(self.dhcpinfo)

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
        self.compslist = [{self.computername: self.dicts['time']}]
        try:
            self.grouppolicy = trg['GroupPolicyinfo']
        except:
            pass
        self.set_dict()

    def check_dict(self, target_dict):
        Comp.check_dict(self, target_dict)
        self.compslist.extend(target_dict['compslist'])

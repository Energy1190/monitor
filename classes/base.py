import sys
import time
import datetime
from system.system import return_nub
from classes.db_mongo import Database

class Base():
    def __init__(self, mainfild=None, output=sys.stdout, error=sys.stderr):
        self.mainfild = (mainfild or 'name')    # Определяет ключ, по которому будет происходить поиск в базе данных
        self.output = output                    # Определяет stdout
        self.error = error                      # Определяет stderr
        self.exist = False
        print("A new class object was created. Class: {0}".format(str(self.__class__.__name__)), file=self.output)
        self.obj = {}
        self.database = None

    def set_storage(self, type=None, target=None):
        if type == 'mongoDB':
            self.database = Database(target=target)
        else:
            self.database = type
        method = ['change', 'set', 'get', 'update']
        x = [i for i in method if i not in dir(self.database)]
        if x:
            t = "The selected storage type does not support the necessary operations - {0}".format(", ".join(x))
            print(t, file=self.error)
            raise TypeError(t)
        print("Assigned storage. Class: {0}. Storage: {1}".format(str(self.__class__.__name__), str(type)), file=self.output)

    def set_parameter(self, name=None, val=None):
        self.obj[name] = val

    def get_parameter(self, name=None):
        return self.obj[name]

    def get_object(self, name):
        assert self.mainfild, "Main key value is not specified"
        assert not self.obj, "You can not get an object. Self object is not empty"
        self.database.change(dicts={self.mainfild: name})
        self.obj = self.database.get()
        print("Received object from storage. Object name: {0}. Object contains keys: {1}.".format(str(name), str(list(self.obj))),
              file=self.output)
        return self.obj

    def set_object(self):
        assert self.mainfild, "Main key value is not specified"
        assert not self.exist, "The object already exists in the storage, try use the update method"
        self.database.change(dicts={self.mainfild: self.obj.get(self.mainfild)})
        self.database.set(self.obj)
        print("The object is stored in the storage. Object name: {0}".format(str(self.obj.get(self.mainfild))),
              file=self.output)
        return self.obj

    def update_object(self):
        assert self.mainfild, "Main key value is not specified"
        self.database.change(dicts={self.mainfild: self.obj.get(self.mainfild)})
        self.database.update(self.obj)
        print("The object in the storage has been updated. Object name: {0}".format(str(self.obj.get(self.mainfild))),
              file=self.output)

    def check_object(self, name, get=None):
        assert self.mainfild, "Main key value is not specified"
        self.database.change(dicts={self.mainfild: name})
        x = self.database.get()
        if x:
            self.exist = True
        else:
            self.exist = False

    def generate_from_list(self, list_object, name, time=None, custom=None):
        x = []
        for i in list_object:
            for j in i:
                self.set_parameter(name=j, val=i[j])
                if self.check_object(j):
                    self.update_object()
                else:
                    self.set_object()
            x.append(self.obj)
            self.obj = {}
        print("{0} objects added to and generated in the repository".format(str(len(list_object))), file=self.output)
        return {'name': name, 'data': x, 'time': time, 'custom': custom}

    def set_main(self, data_object):
        return False

class User(Base):
    def set_main(self, data_object):
        self.mainfild = 'username'
        self.set_parameter(name='username', val=str(data_object['Userinfo']['Username']).lower())
        self.set_parameter(name='domain', val=str(data_object['Userinfo']['Domainname']).lower())
        self.set_parameter(name='computername', val=str(data_object['Userinfo']['Computername']).lower())
        self.set_parameter(name='grouppolicy', val=str(data_object.get('GroupPolicyinfo')))
        self.set_parameter(name='ps_version', val=str(data_object.get('Version')))
        self.set_parameter(name='time', val=time.gmtime((return_nub(data_object['Timeinfo']) + 10800000) / 1000.))
        return True

class Comp(Base):
    def set_main(self, data_object):
        self.mainfild = 'computername'
        self.set_parameter(name='computername', val=str(data_object['Userinfo']['Computername']))
        self.set_parameter(name='system', val=data_object.get('Systeminfo'))
        self.set_parameter(name='hard', val=data_object.get('Harddriveinfo'))
        self.set_parameter(name='disk', val=data_object.get('Diskinfo'))
        self.set_parameter(name='net', val=data_object.get('Networkinfo'))
        self.set_parameter(name='groups', val=data_object.get('Groupsinfo'))
        self.set_parameter(name='error', val=data_object.get('Errorinfo'))
        self.set_parameter(name='program', val=data_object.get('Programsinfo'))
        self.set_parameter(name='service', val=data_object.get('Serviceinfo'))
        self.set_parameter(name='task', val=data_object.get('Tasksinfo'))
        self.set_parameter(name='ps_version', val=data_object.get('Version'))
        self.set_parameter(name='time', val=time.gmtime((return_nub(data_object['Timeinfo']) + 10800000) / 1000.))
        return True

class Dhcp(Base):
    def set_main(self, data_object):
        return None

    def generate_main_list(self, list_object):
        """Метод выводит более удобочитаемый список на основании полученного JSON-объекта.
        И сортирует полученный список по IP-адресам.
        """
        return sorted([{'name': list_object['name'][i],
                        'ip': list_object['ip'][i]['IPAddressToString'],
                        'mac': list_object['mac'][i],
                        'endtime': (lambda x=list_object['timeend'][i]: time.gmtime((return_nub(x) + 10800000)/1000.) if x else x)(),
                        'time': time.gmtime((return_nub(list_object.get("Timeinfo")) + 10800000)/1000.),
                        'rezervation': list_object['rezervation'][i]} for i in range(0, len(list_object['name']))],
                      key=lambda y: y['ip'])

class Route(Base):
    def set_main(self, data_object):
        assert data_object.get('message'), "Empty message."
        assert data_object.get('time'), "No time set."
        x = data_object['message'].split(sep=' ')
        name = x[0][:-1]
        x.remove(x[0])
        self.obj = {i.split(sep='=')[0]: i.split(sep='=')[1] for i in x if len(i.split(sep='=')) > 1}
        self.set_parameter(name='name', val=name)
        if type(data_object['time']) == time.struct_time:
            self.set_parameter(name='time', val=time.strftime('%d.%m.%Y %H:%M:%S', data_object['time']))
            data_object['time'] = datetime.datetime.fromtimestamp(time.mktime(data_object['time']))
        else:
            self.set_parameter(name='time',val=str(data_object['time']))
            self.set_parameter(name='year', val=str(data_object['time'].year))
            self.set_parameter(name='month', val=str(data_object['time'].month))
            self.set_parameter(name='day', val=str(data_object['time'].day))
            self.set_parameter(name='hour', val=str(data_object['time'].hour))
            self.set_parameter(name='min', val=str(data_object['time'].minute))
        return True
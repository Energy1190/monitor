import ipcalc
from classes.base import Base
from classes.db_mongo import Database
from system.logmodule import logger

class Iptable():
    def __init__(self, target=None, net=None, names=None, users=None):
        self.net = (net or '172.16.0.0/19')
        self.target = target
        self.iplist = self.generate_iplist()
        self.db = Database(target=self.target)
        self.names = (names and Database(target=names))
        self.users = (users and Database(target=users))
        self.set_or_update()

    def generate_iplist(self):
        x = ipcalc.Network(self.net)
        return [str(i) for i in x]

    def get_name(self):
        if self.names:
            x = self.names.find()
            for i in self.iplist:
                for j in x:
                    if str(i) == str(j['ip']):
                        i = {'name': str(j('name')), 'ip': i}
                    else:
                        i = {'name': None, 'ip': i}

    def get_users(self):
        logger.debug('User generate for IPTABLE')
        if self.users:
            x = self.users.find()
            logger.debug('Users base is {0}'.format(str(x)))
            for i in self.iplist:
                for j in x:
                    if str(i).split(sep='.')[0] == str(j['computername']):
                        i['user'] = str(j['username'])
                    else:
                        i['user'] = None

    def set_or_update(self):
        logger.debug('Complete generate IPTABLE')
        logger.debug('Object {0}'.format(str(self.iplist)))
        x = self.db.get()
        logger.debug('Current object in base is {0}'.format(str(x)))
        if x:
            self.db.change(dicts=x)
            self.db.update(self.iplist)
        else:
            self.db.set(self.iplist)

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
                        self.update(dsttrg={'name': i}, srctrg={'name': i, 'vals': y}, target=target)
                    elif not x:
                        y = {'name': i, 'vals': []}
                        y['vals'].append(str(self.dicts[i]))
                        self.set(y, target=target)

    def set_dict(self):
        Base.set_dict(self)
        del self.dicts['old']
        del self.dicts['exeption']
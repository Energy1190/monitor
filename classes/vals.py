import ipcalc
from classes.base import Base
from classes.db_mongo import Database

class Iptable():
    def __init__(self, target=None, net=None, names=None, users=None):
        self.net = (net or '172.16.0.0/19')
        self.target = target
        self.db = Database(target=self.target)
        self.names = (names and Database(target=names))
        self.users = (users and Database(target=users))
        self.iplist = self.generate_iplist()
        self.set_or_update()

    def generate_iplist(self):
        x = ipcalc.Network(self.net)
        return [{'ip': str(i),
                 'name': self.get_name(str(i)),
                 'user': self.get_users(self.get_name(str(i)))} for i in x]

    def get_name(self, ip):
        x = list(self.names.find())
        if self.names and x:
            for i in x:
                if str(ip) == str(i['ip']):
                    return i['name']
        return None

    def get_users(self, name):
        x = list(self.users.find())
        if self.users and x:
            for i in x:
                if str(i['name']).split(sep='.')[0].lower() == str(i['computername']).lower():
                    return str(i['username'])
        return None

    def set_or_update(self):
        try:
            x = list(self.db.find())
        except:
            x = []
        if x:
            self.db.delete_all()
        for i in self.iplist:
            self.db.set(i)

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
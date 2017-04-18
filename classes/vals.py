import ipcalc
from system.logmodule import logger
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
                if str(name).split(sep='.')[0].lower() == str(i['computername']).lower():
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

class Vals():
    def __init__(self):
        if self.__class__.__name__ == "Vals":
            Vals.vals_list = list(Database(target=['systems', 'vals']).find())
        self.exeption = ['_id', 'origsent', 'termsent', 'time', 'year', 'month', 'day', 'hour', 'min', 'second']

    def update(func):
        def wraper(self, *args, **kwargs):
            try:
                trg = func(self, *args, **kwargs)
                logger.debug('Fail: ' + str(args) + ' ' + str(kwargs))
            except:
                trg = [None,None,None]
            if trg[1]:
                Database(target=self.target, dicts={'name': trg[0]['name']}).update(trg[0])
            if not trg[2]:
                Vals.vals_list.append(trg[0])
            else:
                Vals.vals_list[trg[2]] = trg[0]
            return trg
        return wraper

    def check(self, trg):
        if trg:
            return [self.analyze_trg(i, trg[i]) for i in trg if i not in self.exeption]

    @update
    def analyze_trg(self, name, val):
        c = False
        x = self.get_item_for_list(name)
        if x and not x[0]['vals'].count(val):
            x[0]['vals'].append(val)
            c = True
        return [{'name': name, 'vals': x[0]['vals']}, c, x[1]]

    def get_item_for_list(self, name):
        for i in range(0, len(Vals.vals_list)):
            try:
                if Vals.vals_list[i].get('name') == name:
                    return [Vals.vals_list[i], i]
            except:
                return [{'name': name, 'vals': None}, 0]
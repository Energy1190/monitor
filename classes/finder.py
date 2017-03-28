from classes.db_mongo import Database

class Finder():
    pass

class Router(Finder):
    var = ['level', 'name', 'id', 'prio', 'event', 'action', 'rev', 'conntime', 'rule', 'recvif'
           'connipproto', 'conn', 'connrecvif', 'conndestif', 'connsrcip', 'connsrcport', 'conndestip',
           'conndestport', 'origsent', 'termsent']

    def __init__(self):
        self.target = ['systems', 'vals']
        self.get_var()
        self.get_val()

    def get_var(self):
        for i in Database(target=self.target).find():
            if i['name'] not in self.var:
                self.var.append(i['name'])

    def get_val(self):
        x = {}
        for i in self.var:
            t = Database(target=self.target, fild='name', fild_var=i).get()
            if t:
                x[i] = t['vals']
            else:
                x[i] = []
        self.var = x

class Trafic(Finder):
    pass
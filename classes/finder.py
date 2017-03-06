from db import db_find, db_get

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
        for i in db_find( target=self.target):
            if i['name'] not in self.var:
                self.var.append(i['name'])

    def get_val(self):
        x = {}
        for i in self.var:
            if dict(db_get(i, target=self.target, fild='name')).get('vals'):
                x[i] = db_get(i, target=self.target, fild='name')['vals']
            else:
                x[i] = []
        self.var = x

class Trafic(Finder):
    pass
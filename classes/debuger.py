
########################################################################################################################

import datetime

VALS_DATA = [{'name': 'prio', 'vals': ['1']}, {'name': 'id', 'vals': ['00600005']}, {'name': 'rev', 'vals': ['1']},
        {'name': 'event', 'vals': ['conn_close_natsat']}, {'name': 'action', 'vals': ['close']},
        {'name': 'rule', 'vals': ['allow_DNS_queryes']}]
VALS_INCOMING1 = {'prio': '1', 'id': '00600005', 'rev': '1', 'event': 'conn_close_natsat', 'action': 'close', 'rule': 'allow_DNS_queryes',
             'conn': 'close', 'connipproto': 'UDP', 'connrecvif': 'lan', 'connsrcip': '172.16.10.10', 'connsrcport': '50435',
             'conndestif': 'wan1', 'conndestip': '192.42.93.30', 'conndestport': '53', 'connnewsrcip': '82.138.27.154',
             'connnewsrcport': '10024', 'connnewdestip': '192.42.93.30', 'connnewdestport': '53', 'origsent': '73',
             'termsent': '708', 'conntime': '131', 'name': 'CONN', 'level': 'info', 'time': datetime.datetime(2017, 4, 4, 9, 41, 19),
             'year': 2017, 'month': 4, 'day': 4, 'hour': 9, 'min': 41, 'second': 19}

VALS_INCOMING2 = {'prio': '1', 'id': '00600006', 'rev': '1', 'event': 'conn_close_natsat', 'action': 'close', 'rule': 'allow_lan_wan1_HTTP_out',
             'conn': 'close', 'connipproto': 'TCP', 'connrecvif': 'lan', 'connsrcip': '172.16.0.26',
             'connsrcport': '54713', 'conndestif': 'wan1', 'conndestip': '81.19.88.81', 'conndestport': '80',
             'connnewsrcip': '82.138.27.154', 'connnewsrcport': '17113', 'connnewdestip': '81.19.88.81', 'connnewdestport': '80',
             'origsent': '1057', 'termsent': '35535', 'conntime': '87', 'name': 'CONN', 'level': 'info',
             'time': datetime.datetime(2017, 4, 6, 14, 40, 26), 'year': 2017, 'month': 4, 'day': 6, 'hour': 14, 'min': 40, 'second': 26}

from classes.vals import Vals

class DebugVals(Vals):
    target = ['tests', 'vals']
    Vals.vals_list = VALS_DATA[:]
    send_to_base = []
    def update(func):
        def wraper(self, *args, **kwargs):
            try:
                trg = func(self, *args, **kwargs)
            except:
                trg = [None,None,None]
            if trg[1]:
                DebugVals.send_to_base.append(trg[0])
            if not trg[2]:
                Vals.vals_list.append(trg[0])
            else:
                Vals.vals_list[trg[2]] = trg[0]
            return trg
        return wraper

    @update
    def analyze_trg(self, name, val):
        c = False
        x = self.get_item_for_list(name)
        if x and not x[0]['vals'].count(val):
            x[0]['vals'].append(val)
            c = True
        return [{'name': name, 'vals': x[0]['vals']}, c, x[1]]


# x = DebugVals()
# x.check(VALS_INCOMING1)
# x.check(VALS_INCOMING2)
# print(x.send_to_base)

########################################################################################################################

CRYPT_DATA = {"Key":"Nv3xx0NAqfrxNqa6q+j5YzTrRs1svLtBCAti1Hp45r0=","Body":b"""0dqII4qHyPi905t9zIdH/5bFM5GthoeQAvB+HZH5M/nbkXgwosNrvfTgiz/bwuE
8Ezxa/iX6xNcOQVWD98u9Rw==""","Crypt":"true","Targets":"report"}

from classes.crypts import Crypt

class DebugCrypt(Crypt):
    pass

# x = DebugCrypt()
# x.set_key(CRYPT_DATA["Key"])
# y = x.remove_end(CRYPT_DATA["Body"])
# print(y)

########################################################################################################################

from classes.base import Base

class ObjectDatabase():
    def __init__(self, obj={}):
        self.obj = obj
    def change(self, *args, **kwargs):
        pass

    def set(self, x):
        self.obj = x

    def get(self):
        return self.obj

    def update(self):
        self.obj = x

class DebugBase(Base):
    pass

# t = ObjectDatabase(obj={'age': 38})
# x = DebugBase(mainfild='name')
# x.set_storage(t)
# print(x.get_object(38))
# x.set_parameter(name='name', val='Mark')
# x.get_parameter('name')
# if x.check_object('name'):
#    x.update_object(x.obj)
# if print(x.set_main(x.obj)):
#    print(t.get())

########################################################################################################################
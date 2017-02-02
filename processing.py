import datetime
from db import db_find
from requests_s import Statistic
from reguests_db import get_route_info_database

def processing_statistics_route(target_dhcp, target_stat, times='hour'):
    x = db_find(target=target_dhcp, limit=1000)
    r = []
    dx = {}
    dx['conndestif'] = 'wan1'
    dx['connrecvif'] = 'lan'
    if times == 'hour':
        dx['start_time'] = datetime.datetime.now().timetuple()[0:4] - datetime.timedelta(hours=1)
        dx['deep'] = 4
    elif times == 'day':
        dx['start_time'] = datetime.datetime.now()
        dx['deep'] = 3
    for i in x:
        dx['connsrcip'] = i['ip']
        y = Statistic(get_route_info_database(**dx), target=target_stat)
        y.set_dict()
        r.append(y.dicts)
    y.set({'stat': r, 'time': datetime.datetime.now().timetuple()[0:3], 'inter': times})

if __name__ == '__main__':
    pass
import datetime
from db import db_find
from traceback import format_exc
from system import consol_log
from requests_s import Statistic
from reguests_db import get_route_info_database

def processing_statistics_route(target_dhcp, target_stat, times='hour'):
    try:
        consol_log('Start generate statistics from router base per {0}'.format(times), level='info')
        x = db_find(target=target_dhcp, limit=1000)
        consol_log('Get data from collection {0}. Example data: \n {1}'.format(target_dhcp, x[0]), level='debug')
        r = []
        dx = {}
        dx['conndestif'] = 'wan1'
        dx['connrecvif'] = 'lan'
        if times == 'hour':
            dx['start_time'] = (datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:4]
            dx['deep'] = 4
        elif times == 'day':
            dx['start_time'] = (datetime.datetime.now() + datetime.timedelta(hours=3))
            dx['deep'] = 3
        for i in x:
            dx['connsrcip'] = i['ip']
            y = Statistic(get_route_info_database(**dx), i['ip'], target=target_stat)
            y.set_dict()
            r.append(y.dicts)
        consol_log('Complete generate result. Example data: \n {0}'.format(r[0]), level='debug')
        y.set({'stat': r, 'time': datetime.datetime.now().timetuple()[0:dx['deep']], 'inter': times})
        consol_log('Successful set result in {0}'.format(target_stat), level='debug')
        consol_log('Successful end generate statistics from router base per {0}'.format(times), level='info')
    except Exception as err:
        consol_log('Fail processing generate statistics from router base per {0}. Error : {1}'.format(times, str(err)),
                   trace=format_exc(), level='error')
if __name__ == '__main__':
    pass
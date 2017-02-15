import datetime
from db import db_find
from traceback import format_exc
from logmodule import logger
from requests_s import Statistic
from reguests_db import get_route_info_database

def processing_statistics_route(target_dhcp, target_stat, times='hour'):
    try:
        logger.info('Start generate statistics from router base per {0}'.format(times))
        x = db_find(target=target_dhcp, limit=1000)
        logger.debug('Get data from collection {0}. Example data: \n {1}'.format(target_dhcp, x[0]))
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
        logger.debug('Complete generate result. Example data: \n {0}'.format(r[0]))
        y.set({'stat': r, 'time': datetime.datetime.now().timetuple()[0:dx['deep']], 'inter': times})
        logger.debug('Successful set result in {0}'.format(target_stat))
        logger.info('Successful end generate statistics from router base per {0}'.format(times))
    except Exception as err:
        logger.error('Fail processing generate statistics from router base per {0}. Error : {1}'.format(times, str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))
if __name__ == '__main__':
    pass
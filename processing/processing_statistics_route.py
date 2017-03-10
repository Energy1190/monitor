import datetime
from db import db_find, db_get, db_set, db_update
from system import sizeof_fmt
from traceback import format_exc
from logmodule import logger
from requests_s import Statistic
from reguests_db import get_route_info_database
from classes.dictory import Stat

def main(target_dhcp, target_stat, times=(datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:4],
         date=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple()[0:3]):
    try:
        logger.info('Start generate statistics from router base per {0}'.format((datetime.datetime.now() + datetime.timedelta(hours=2))))
        x = db_find(target=target_dhcp, limit=1000)
        logger.debug('Get data from collection {0}. Example data: \n {1}'.format(target_dhcp, x[0]))
        r = []
        dx = {}
        dx['conndestif'] = 'wan1'
        dx['connrecvif'] = 'lan'
        dx['start_time'] = times
        dx['end_time'] = dx['start_time']
        dx['deep'] = 4
        for i in x:
            logger.debug('Start generate statistics for {0}'.format(i['ip']))
            dx['connsrcip'] = i['ip']
            y = Statistic(get_route_info_database(**dx), i['ip'], i['name'], target=target_stat)
            y.set_dict()
            r.append(y.dicts)
        logger.debug('Complete generate result. Example data: \n {0}'.format(r[0]))
        results = {'stat': r, 'time': dx['start_time'], 'inter': 'hour'}
        y.set(results)
        logger.debug('Successful set result in {0}'.format(target_stat))
        logger.info('Successful end generate statistics from router base per {0}'.format((datetime.datetime.now() + datetime.timedelta(hours=2))))
        processing_statistics_route_per_day(target_dhcp, target_stat, results, date)
    except Exception as err:
        logger.error('Fail processing generate statistics from router base per {0}. Error : {1}'.format(datetime.datetime.now() + datetime.timedelta(hours=2), str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

def processing_statistics_route_per_day(target_dhcp, target_stat, result, date, times):
    logger.info('Start sum day stat')
    logger.debug('Date is {0}'.format(str(tuple(date))))
    logger.debug('Result is {0}'.format(str(result)))
    try:
        x = db_get(tuple(date), target=target_stat, fild='time')
        if not x:
            result['inter'] = 'day'
            result['time'] = tuple(date)
            db_set(result, target=target_stat)
        else:
            a = [Stat(i) for i in x.get('stat')]
            b = [Stat(i) for i in result.get('stat')]
            c = [i+j for i in a for j in b if str(i['ip']) == str(j['ip'])]
            result = {'stat': c, 'time': date, 'inter': 'day'}
            logger.debug('SUM is {0}'.format(str(c)))
            db_update(result, target=target_stat, fild={'time': date})
        check_empty_hours(target_dhcp, target_stat, date, times)
        logger.debug('End get is {0}'.format(str(db_get(tuple(date), target=target_stat, fild='time'))))
    except Exception as err:
        logger.error('Fail processing generate statistics from router base per day. Error : {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

def check_empty_hours(target_dhcp, target_stat, date, times):
    x = list(date)
    y = list(times)
    x.append(0)
    for i in range(0, int(y[3])):
        x[3] = i
        y = db_get(tuple(x), target=target_stat, fild='time')
        if not y:
            logger.info('Miss hour {0} start generate'.format(str(i)))
            main(target_dhcp, target_stat, times=tuple(x), date=date)

if __name__ == '__main__':
    pass
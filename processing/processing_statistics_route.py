import datetime
from db import db_find, db_get, db_set
from system import sizeof_fmt
from traceback import format_exc
from logmodule import logger
from requests_s import Statistic
from reguests_db import get_route_info_database

def main(target_dhcp, target_stat):
    try:
        logger.info('Start generate statistics from router base per {0}'.format((datetime.datetime.now() + datetime.timedelta(hours=2))))
        x = db_find(target=target_dhcp, limit=1000)
        logger.debug('Get data from collection {0}. Example data: \n {1}'.format(target_dhcp, x[0]))
        r = []
        dx = {}
        dx['conndestif'] = 'wan1'
        dx['connrecvif'] = 'lan'
        dx['start_time'] = (datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:4]
        dx['end_time'] = dx['start_time']
        dx['deep'] = 4
        for i in x:
            logger.debug('Start generate statistics for {0}'.format(i['ip']))
            dx['connsrcip'] = i['ip']
            y = Statistic(get_route_info_database(**dx), i['ip'], i['name'], target=target_stat)
            y.set_dict()
            r.append(y.dicts)
        logger.debug('Complete generate result. Example data: \n {0}'.format(r[0]))
        y.set({'stat': r, 'time': dx['start_time'], 'inter': 'hour'})
        logger.debug('Successful set result in {0}'.format(target_stat))
        logger.info('Successful end generate statistics from router base per {0}'.format((datetime.datetime.now() + datetime.timedelta(hours=2))))
        if (datetime.datetime.now() + datetime.timedelta(hours=3)).hour == 0:
            processing_statistics_route_per_day(target_stat)
    except Exception as err:
        logger.error('Fail processing generate statistics from router base per {0}. Error : {1}'.format(datetime.datetime.now() + datetime.timedelta(hours=2), str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

def processing_statistics_route_per_day(target_stat):
    try:
        day = (datetime.datetime.now() + datetime.timedelta(hours=3) - datetime.timedelta(hours=1)).timetuple()[0:3]
        logger.info('Start generate statistics from router base per day: {0}'.format(str(day)))
        r = []
        for i in range(24):
            x = list(day)
            x.append(i)
            r.append(db_get(tuple(x), target=target_stat, fild='time'))
        x = [{'in': j['data']['in_bytes'], 'out': j['data']['out_bytes'], 'ip': j['ip']} for i in r if i and i.get('stat')
             for j in i['stat'] if j['data'].get('in_bytes') and j['data'].get('out_bytes')]
        r = {}
        for i in x:
            if i['ip'] not in r:
                r[i['ip']] = {'out':i['out'], 'in': i['in']}
            elif i['ip'] in r:
                r[i['ip']]['out'] = r[i['ip']]['out'] + i['out']
                r[i['ip']]['in'] = r[i['ip']]['in'] + i['in']
        for i in r:
            r[i]['in'] = sizeof_fmt(r[i]['in'])
            r[i]['out'] = sizeof_fmt(r[i]['out'])
        x = [{'ip': i, 'data': {'in': r[i]['in'], 'out': r[i]['out']}} for i in r]
        db_set({'stat': x, 'time': day, 'inter': 'day'}, target=target_stat)
        logger.info('Successful end generate statistics from router base per day: {0}'.format(str(day)))
    except Exception as err:
        logger.error('Fail processing generate statistics from router base per day. Error : {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

if __name__ == '__main__':
    pass
import datetime
from db import db_find, db_get, db_set, db_update
from traceback import format_exc
from logmodule import logger
from reguests_db import get_route_info_database
from classes.route import Stat
from classes.db_mongo import Database

class Statistics():
    def __init__(self, target, target_stat, times=None, date=None, **kvargs):
        self.dx = kvargs
        logger.debug('Incomig dict {0}'.format(str(self.dx)))
        self.result = []
        self.times = (times or (datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:4])
        self.date = (date or (datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:3])
        self.iplist = Database(target=target)
        self.body = {'stat': self.result, 'time': times, 'inter': 'hour'}
        self.daystat = Database(target=target_stat)
        self.dx['start_time'] = (kvargs.get('start_time') or times)
        self.dx['end_time'] = (kvargs.get('end_time') or times)

    def set(self):
        logger.debug('Ad stat {0}'.format(str(self.body)))
        logger.debug('When result is {0}'.format(str(self.result)))
        logger.debug('Element result is {0}'.format(str(self.result[0])))
        logger.debug('And type is {0} - {1} - {2}'.format(type(self.body), type(self.result), type(self.result[0])))
        self.daystat.set(self.body)

    def set_day(self, x):
        self.daystat.change(fild='time', fild_var=self.date)
        self.daystat.update(x)

    def generate(self):
        for i in self.iplist.find():
            self.dx['connsrcip'] = i['ip']
            y = Stat(get_route_info_database(**self.dx), i['ip'], i['name'], ['clients','users'])
            self.result.append(y.trg)

    def per_day(self):
        self.daystat.change(fild='time', fild_var=self.date)
        x = self.daystat.get()
        if x:
            a = [Stat(dicts=i) for i in x.get('stat')]
            b = [Stat(dicts=i) for i in self.body.get('stat')]
            c = [i + j for i in a for j in b if str(i['ip']) == str(j['ip'])]
            return {'stat': c, 'time': self.date, 'inter': 'day'}
        else:
            self.body['time'] = self.date
            self.body['inter'] = 'day'
            return False

def main(target_dhcp, target_stat, times=None, date=None):
    logger.info(logger.info('Start generate statistics from router base per hour'))
    try:
        x = Statistics(target_dhcp, target_stat, times=times, date=date, conndestif='wan1', connrecvif='lan')
        x.generate()
        x.set()
        y = x.per_day()
        if y:
            x.set_day(y)
        else:
            x.set()
        check_empty_hours(target_dhcp, target_stat, x.date, x.times)
    except Exception as err:
        logger.error('Fail processing generate statistics from router base per {0}. Error : {1}'.format(
            datetime.datetime.now() + datetime.timedelta(hours=2), str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

def main_old(target_dhcp, target_stat, times=None, date=None):
    if not times:
        times=(datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:4]
    if not date:
        date=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple()[0:3]
    try:
        logger.info('Start generate statistics from router base per {0}'.format(str(times)))
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
            y = Stat(get_route_info_database(**dx), i['ip'], i['name'], ['clients','users'])
            r.append(y.trg)
        logger.debug('Complete generate result. Example data: \n {0}'.format(r[0]))
        results = {'stat': r, 'time': dx['start_time'], 'inter': 'hour'}
        Database(target=target_stat).set(results)
        logger.debug('Successful set result in {0}'.format(target_stat))
        logger.info('Successful end generate statistics from router base per {0}'.format((datetime.datetime.now() + datetime.timedelta(hours=2))))
        processing_statistics_route_per_day(target_dhcp, target_stat, results, date, times)
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
            a = [Stat(dicts=i) for i in x.get('stat')]
            b = [Stat(dicts=i) for i in result.get('stat')]
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
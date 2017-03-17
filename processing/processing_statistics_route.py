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
        self.dx['start_time'] = (kvargs.get('start_time') or times or self.times)
        self.dx['end_time'] = (kvargs.get('end_time') or times or self.times)

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
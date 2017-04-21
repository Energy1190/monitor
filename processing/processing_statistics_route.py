import sys
import datetime
from traceback import format_exc
from classes.db_mongo import Database
from classes.route import Stat
from system.requestus import get_route_info_database

class Statistics():
    def __init__(self, target, target_stat, times=None, date=None, output=sys.stdout, error=sys.stderr, **kvargs):
        self.output = output
        self.error = error
        self.dx = kvargs
        self.result = []
        self.times = (times or (datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:4])
        self.date = (date or (datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple()[0:3])
        self.target = target_stat
        self.iplist = Database(target=target)
        self.daystat = Database(target=target_stat)
        self.dx['start_time'] = (kvargs.get('start_time') or times or self.times)
        self.dx['end_time'] = (kvargs.get('end_time') or times or self.times)
        self.incomplete = False
        self.nozero = False
        self.full = False
        self.body = {'stat': self.result, 'time': times, 'inter': 'hour', 'incomplete': self.incomplete, 'nozero': self.nozero,
                     'full': self.full}
        print('A new class of statistics was generated', file=output)
        print('Body of the class - {0}'.format(str(self.body)), file=output)

    def check(self):
        target_collection = 'base-{0}-{1}-{2}'.format(self.times[0],
                                                      self.times[1],
                                                      self.times[2])
        hour = self.times[3]
        incoming = Database(target=['route', 'info']).get()
        target = Database(target=['route', target_collection], dicts={'hour': hour}).get()
        full = Database(target=self.target, dicts={'time': self.date}).get().get('full')
        self.full = full
        if incoming and incoming.get('time') and type(incoming.get('time')) == datetime.datetime:
            x = incoming.get('time')
            if x.day == self.times[2]:
                self.incomplete = True
        print('A number of inspections were carried out', file=self.output)
        print('Incomplete: {0}, full: {1}, target: {2}'.format(str(self.incomplete),
                                                               str(self.full),
                                                               str(target)), file=self.output)
        if not target:
            return False
        return True

    def check_zero(self):
        for i in self.result:
            if i['data']['in_bytes'] or i['data']['out_bytes']:
                self.nozero = True
        print('A check for data was performed. Data: {0}'.format(str(self.nozero)), file=self.output)

    def set(self, no_replase):
        if no_replase:
            no_replase = False
            self.daystat.set(self.body)
        else:
            no_replase = True
            self.daystat.change(dicts={'time': self.times})
            self.daystat.update(self.body)
        print('The data was recorded in the database. Updated: {0}.'.format(str(no_replase)), file=self.output)

    def set_day(self, x):
        self.daystat.change(fild='time', fild_var=self.date)
        self.daystat.update(x)
        print('Data for the day were updated and written to the database.', file=self.output)

    def generate(self):
        for i in self.iplist.find():
            self.dx['connsrcip'] = i['ip']
            y = Stat(get_route_info_database(**self.dx), i['ip'], i['name'], ['clients','users'])
            self.result.append(y.trg)
        print('The statistics for {0} objects were generated'.format(str(len(self.result))), file=self.output)
        self.check_zero()

    def remove_day(self):
        self.daystat.change(fild='time', fild_var=self.date)
        print('Entry for {0} has been deleted'.format(str(self.date)), file=self.output)
        return self.daystat.delete()

    def per_day(self):
        self.daystat.change(fild='time', fild_var=self.date)
        x = self.daystat.get()
        if x:
            a = [Stat(dicts=i) for i in x.get('stat')]
            b = [Stat(dicts=i) for i in self.body.get('stat')]
            c = [i + j for i in a for j in b if str(i['ip']) == str(j['ip'])]
            return {'stat': c, 'time': self.date, 'inter': 'day', 'incomplete': self.incomplete, 'nozero': self.nozero,
                    'full': self.full}
        else:
            self.body['time'] = self.date
            self.body['inter'] = 'day'
            return False

    def __add__(self, other):
        result = []
        try:
            y = other.body['stat']
        except:
            y = other['stat']

        for i in self.body['stat']:
            x = Stat(dicts=i)
            for j in y:
                if str(j.get('ip')) == str(x.trg['ip']):
                    xx = Stat(dicts=j)
                    result.append(x+xx)

        if len(result) == len(self.body['stat']):
            return {'stat': result, 'time': self.date, 'inter': 'day', 'incomplete': self.incomplete, 'nozero': self.nozero}
        else:
            return self.body

def main(target_dhcp, target_stat, times=None, date=None, noreplase=True, full=False, output=sys.stdout, error=sys.stderr):
    print('--'*20, file=output)
    print('Start of statistics generation', file=output)
    print('Incoming time - {0} and date - {1}'.format(str(times), str(date)), file=output)
    try:
        x = Statistics(target_dhcp, target_stat, times=times, date=date, conndestif='wan1', connrecvif='lan')
        if x.check():
            print('In the target database, data is found', file=output)
            x.full = full
            x.generate()
            x.set(noreplase)
            y = x.per_day()
            if y:
                x.set_day(y)
            else:
                x.set(True)
            print('Statistics generated, start post-check', file=output)
        check_empty_hours(target_dhcp, target_stat, x.date, x.times, output=output, error=error)
        check_incomplete(target_dhcp, target_stat, x.date, x.times, output=output, error=error)
        check_extra_entries(target_stat, x.date)
    except Exception as err:
        print('An error occurred while generating statistics.', file=error)
        print(str(format_exc()), file=error)

def check_empty_hours(target_dhcp, target_stat, date, times, output=sys.stdout, error=sys.stderr):
    print('Run a check for missing entries in the database', file=output)
    x = list(date)
    y = list(times)
    x.append(0)
    print('Need to check {0} objects.'.format(str(y[3])), file=output)
    for i in range(0, int(y[3])):
        x[3] = i
        y = Database(target=target_stat, fild='time', fild_var=tuple(x)).get()
        try:
            if not y or not y['nozero']:
                print('An empty record was found, dated {0}, initialized the mechanism for generating statistics'.format(str(x)),
                      file=error)
                main(target_dhcp, target_stat, times=tuple(x), date=date, noreplase=y['nozero'])
        except:
            if not y:
                print('An empty record of the old sample was found, dated {0}, initialize the mechanism for generating statistics'.format(str(x)),
                      file=error)
                main(target_dhcp, target_stat, times=tuple(x), date=date, noreplase=True)

def check_incomplete(target_dhcp, target_stat, date, times, output=sys.stdout, error=sys.stderr):
    print('Run integrity check', file=output)
    x = list(date)
    x[2] = x[2] - 1
    c = Statistics(target_dhcp, target_stat, times=times, date=tuple(x), conndestif='wan1', connrecvif='lan')
    c.check()
    if not c.incomplete and not c.full:
        print('Mismatch detected, start database regeneration', file=output)
        c.remove_day()
        for i in range(0,23):
            x[3] = i
            main(target_dhcp, target_stat, times=tuple(x), date=tuple(x[:-1]), noreplase=False, full=True)

def check_extra_entries(target_stat, date):
    print('Run the check for extra entries', file=sys.stdout)
    x = list(date)
    x.append(0)
    result = []
    c = Database(target=target_stat, dicts={'time': date})

    if c.count(c.find): result.append(c.count(c.find))
    for i in range(0,23):
        x[3] = i
        c.change(dicts={'time': tuple(x)})
        result.append(c.count(c.find))

    if sum(result) > 24:
        print('More records found than allowed - {0}'.format(str(sum(result))), file=sys.stderr)

if __name__ == '__main__':
    pass
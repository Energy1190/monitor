from traceback import format_exc
from logmodule import logger

class Dictory():
    pass

class Stat(Dictory):
    def __init__(self, dicts):
        self.trg = dicts

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def __str__(self):
        return str(self.trg)

    def __getitem__(self, item):
        return self.trg[item]

    def get(self, obj):
        return self.trg.get(obj)

    def __add__(self, other):
        try:
            if str(self.trg['ip']) == str(other['ip']):
                self.trg['counts'] = int(self.trg['counts']) + int(other['counts'])
                if other.get('name') and self.trg.get('name') != other['name']:
                    if self.trg.get('oldname'):
                        self.trg['oldname'].append({self.trg['name']: other['time']})
                    else:
                        self.trg['oldname'] = [{self.trg['name']: other['time']}]
                    self.trg['name'] = other['name']
                if other.get('user') and self.get('user') != other['user']:
                    if self.trg.get('olduser'):
                        self.trg['olduser'].append({self.trg['user']: other['time']})
                    else:
                        self.trg['olduser'] = [{self.trg['user']: other['time']}]
                    self.trg['user'] = other['user']
                if self.trg['data'].get('in_bytes') and self.trg['data'].get('out_bytes'):
                    logger.debug('Vars - self: {0} and  over: {1}'.format(str(self.trg['data']['in_bytes']), str(other['data'].get('in_bytes'))))
                    self.trg['data']['in_bytes'] = int(self.trg['data']['in_bytes']) + int(other['data'].get('in_bytes') or 0)
                    self.trg['data']['out_bytes'] = int(self.trg['data']['out_bytes']) + int(other['data'].get('out_bytes') or 0)
                    self.trg['data']['in'] = self.sizeof_fmt(self.trg['data']['in_bytes'])
                    self.trg['data']['out'] = self.sizeof_fmt(self.trg['data']['out_bytes'])
                    logger.debug('End vars {0} and {1}'.format(str(self.trg['data']['in_bytes']), str(self.trg['data']['out_bytes'])))
                return self.trg
        except:
            logger.error('Fail sum Statistics.')
            logger.error(str(format_exc()))

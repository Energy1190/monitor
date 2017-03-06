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

    def __add__(self, other):
        try:
            if str(self.trg['ip']) == str(other['ip']):
                self.trg['counts'] = int(self.trg['counts']) + int(other['counts'])
                if self.trg['name'] != other['name']:
                    if self.trg.get('oldname'):
                        self.trg['oldname'].append({self.trg['name']: other['time']})
                    else:
                        self.trg['oldname'] = [{self.trg['name']: other['time']}]
                    self.trg['name'] = other['name']
                if self.trg['user'] != other['user']:
                    if self.trg.get('olduser'):
                        self.trg['olduser'].append({self.trg['user']: other['time']})
                    else:
                        self.trg['olduser'] = [{self.trg['user']: other['time']}]
                    self.trg['user'] = other['user']
                self.trg['data']['in_bytes'] = self.trg['data']['in_bytes'] + other['data']['in_bytes']
                self.trg['data']['out_bytes'] = self.trg['data']['out_bytes'] + other['data']['out_bytes']
                self.trg['data']['in'] = self.sizeof_fmt(self.trg['data']['in_bytes'])
                self.trg['data']['out'] = self.sizeof_fmt(self.trg['data']['out_bytes'])
                return self.trg
        except:
            logger.error('Fail sum Statistics.')
            logger.error(str(format_exc()))

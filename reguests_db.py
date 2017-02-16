from db import db_find
from traceback import format_exc
from logmodule import logger
import datetime

def get_time_tuple(time_str):
    try:
        return datetime.datetime(*tuple(map(lambda x: int(x), time_str.split(sep='_'))))
    except ValueError:
        return (datetime.datetime.now() + datetime.timedelta(hours=3))
    except AttributeError:
        return datetime.datetime(*time_str)

def get_time_requests(start_time, end_time, deep=4):
    try:
        logger.debug('Generate time')
        r = []
        x = start_time.timetuple()[0:deep]
        y = end_time.timetuple()[0:deep]
        logger.debug('The initial values: {0} and {1}'.format(str(x), str(y)))
        while x != y:
            if x not in r:
                r.append(x)
            start_time = start_time + datetime.timedelta(minutes=1)
            x = start_time.timetuple()[0:deep]
        r.append(x)
        logger.debug('Successful generate time. Example data: {0}'.format(r[0]))
        return r
    except Exception as err:
        logger.error('Fail generate time. Error: {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

def get_answer(dx, target):
    x = []
    y = []
    if type(target[0]) == list:
        for j in target:
            y += db_find(dx, target=j, limit=1000000)
    else:
        y = db_find(dx, target=target, limit=1000000)
    x.append(dx)
    for i in y:
        if i not in x:
            x.append(i)
    return x

def get_route_info_database(*args, start_time=None, end_time=None, deep=4, **kvargs):
    try:
        logger.debug('Start search in the database log')
        x = []
        t = []
        dx = kvargs
        if 'start_time' in dx.keys():
            del dx['start_time']
        if 'end_time' in dx.keys():
            del dx['end_time']
        if 'deep' in dx.keys():
            del dx['deep']
        if start_time and end_time:
            start_time = get_time_tuple(start_time)
            end_time = get_time_tuple(end_time)
        elif start_time:
            start_time = get_time_tuple(start_time)
            end_time = (datetime.datetime.now() + datetime.timedelta(hours=3))
        else:
            start_time = (datetime.datetime.now() + datetime.timedelta(hours=3)) - datetime.timedelta(days=1)
            end_time = (datetime.datetime.now() + datetime.timedelta(hours=3))
        if start_time.timetuple()[2] != end_time.timetuple()[2]:
            ee = end_time.timetuple()
            ss = start_time.timetuple()
            target = [['route', 'base-{0}-{1}-{2}'.format(j,h,i)] for i in range(ss[2],ee[2]+1)
                      for h in range(ss[1],ee[1]+1)
                      for j in range(ss[0],ee[0]+1)]
        elif start_time.timetuple()[0:2] == datetime.datetime.now().timetuple()[0:2]:
            time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
            target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                          time_now.timetuple()[1],
                                                          time_now.timetuple()[2])
            target = ['route', target_collection]
        else:
            ss = start_time.timetuple()
            target = ['route', 'base-{0}-{1}-{2}'.format(ss[0],ss[1],ss[2])]
        logger.debug('Search options: start-time: {0}, end-time{1}'.format(str(start_time),str(end_time)))
        logger.debug('Search base(s): {0}'.format(str(target)))
        t = get_time_requests(start_time, end_time, deep=deep)
        if t:
            for j in t:
                if len(j) >= 1:
                    dx['year'] = j[0]
                if len(j) >= 2:
                    dx['month'] = j[1]
                if len(j) >= 3:
                    dx['day'] = j[2]
                if len(j) >= 4:
                    dx['hour'] = j[3]
                if len(j) >= 5:
                    dx['minute'] = j[4]
                for i in get_answer(dx, target):
                    x.append(i)
            logger.debug('Successful search in the database log')
            return x
    except Exception as err:
        logger.error('Fail search in the database log. Error: {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

if __name__ == '__main__':
    start_time = (2017, 1, 20, 22, 23)
    end_time = (2017, 1, 22, 22, 23)


from db import db_find
import datetime

target_collection ='base-{0}-{1}-{2}'.format((datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple()[0],
                                             (datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple()[1],
                                             (datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple()[2])
def get_time_tuple(time_str):
    try:
        return datetime.datetime(*tuple(map(lambda x: int(x), time_str.split(sep='_'))))
    except ValueError:
        return datetime.datetime.now() + datetime.timedelta(hours=3)
    except AttributeError:
        return datetime.datetime(*time_str)

def get_time_requests(start_time, end_time, deep=4):
    r = []
    x = start_time.timetuple()[0:deep]
    y = end_time.timetuple()[0:deep]
    while x != y:
        if x not in r:
            r.append(x)
        start_time = start_time + datetime.timedelta(minutes=1)
        x = start_time.timetuple()[0:deep]
    r.append(x)
    return r

def get_answer(dx, target):
    x = []
    y = db_find(dx, target=target, limit=1000000)
    x.append(dx)
    for i in y:
        if i not in x:
            x.append(i)
    return x

def get_route_info_database(*args, start_time=None, end_time=None, deep=4, **kvargs):
    dx = kvargs
    t = []
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
        end_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    else:
        start_time = datetime.datetime.now() - datetime.timedelta(days=1) + datetime.timedelta(hours=3)
        end_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    if start_time.timetuple()[2] != end_time.timetuple()[2]:
        ee = end_time.timetuple()
        ss = start_time.timetuple()
        target = [['route', 'base-{0}-{1}-{2}'.format(j,h,i)] for i in range(ss[2],ee[2])
                  for h in range(ss[1],ee[1])
                  for j in range(ss[0],ee[0])]
    elif start_time.timetuple()[0:2] == datetime.datetime.now().timetuple()[0:2]:
        target = target_collection
    else:
        ss = start_time.timetuple()
        target = ['route', 'base-{0}-{1}-{2}'.format(ss[0],ss[1],ss[2])]
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
    if type(target[0]) == list:
        x = []
        for j in target:
            x += get_answer(dx, j)
        return x
    return get_answer(dx, target)

if __name__ == '__main__':
    start_time = (2017, 1, 20, 22, 23)
    end_time = (2017, 1, 22, 22, 23)
    print(type([]))
    if type([]) == list:
        print(get_time_requests(get_time_tuple('2017_1_22_22'),get_time_tuple('2017_2_22_22'), deep=2))
#    print(get_route_info_database(**{'blle':'dsfsdf', 'flll':'sfadsf', 'start_time': (2033, 5, 12, 23, 56), 'end_time':None}))

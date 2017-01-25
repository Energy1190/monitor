from db import db_find
import datetime

def years(x, y, *args):
    x = int(x)
    y = int(y)
    r = []
    while x != y:
        if x > y:
            return False
        r.append(x)
        x += 1
    r.append(x)
    return r

def over(x, y, num, pre=None):
    x = int(x)
    y = int(y)
    r = []
    if pre:
        return [years(x, y)]
    else:
        r.append(years(x, num))
        r.append(years(1, y))
        return r

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
        r.append(x)
        start_time = start_time + datetime.timedelta(minutes=1)
        x = start_time.timetuple()[0:deep]
    r.append(x)
    return r

#def get_time_requests(start_time, end_time):
#    r = []
#    n = 0
#    try:
#        s = datetime.datetime(*start_time)
#    except:
#        s = start_time
#    try:
#        e = datetime.datetime(*end_time)
#    except:
#        e = end_time
#    x = [[int(i), int(j), g] for i, j, g in [(s.year, e.year, 0), (s.month, e.month, 12), (s.day, e.day, 31), (s.hour, e.hour, 60), (s.minute, e.minute, 60)]]
#    f = years(*x[0])
#    r.append(f)
#    if not f[0]:
#        return False
#    for i in range(0, len(x)):
#        try:
#            if i+1 <= len(x) + 1:
#                if len(years(*x[0])) == 1 and i == 0 or i != 0 and len(f[0]) == 1:
#                    f = over(*x[i+1], pre=True)
#                else:
#                    f = over(*x[i+1])
#                if not f[0]:
#                    return False
#                r.append(f)
#        except IndexError:
#            pass
#    rr = []
#    if len(r[-1]) == 1:
#        xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
#        rr = xx
#    else:
#        if len(r[-2]) == 1:
#            xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
#            yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
#            xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
#            rr = xx + yy + xx2
#        else:
#            if len(r[-3]) == 1:
#                xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
#                yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
#                zz = [(r[-5][0], r[-4][0][0], i, 0, 0) for i in r[-3][0]]
#                xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
#                yy2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], i, 0) for i in r[-2][1]]
#                rr = xx + yy + zz + xx2 + yy2
#            else:
#                if len(r[-4]) == 1:
#                    xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
#                    yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
#                    zz = [(r[-5][0], r[-4][0][0], i, 0, 0) for i in r[-3][0]]
#                    cc = [(r[-5][0], i, 0, 0, 0) for i in r[-4][0]]
#                    xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
#                    yy2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], i, 0) for i in r[-2][1]]
#                    zz2 = [(r[-5][-1], r[-4][-1][-1], i, 0, 0) for i in r[-3][1]]
#                    rr = xx + yy + zz + cc + xx2 + yy2 + zz2
#                else:
#                    xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
#                    yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
#                    zz = [(r[-5][0], r[-4][0][0], i, 0, 0) for i in r[-3][0]]
#                    cc = [(r[-5][0], i, 0, 0, 0) for i in r[-4][0]]
#                    vv = [(i, 0, 0, 0, 0) for i in r[-5]]
#                    xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
#                    yy2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], i, 0) for i in r[-2][1]]
#                    zz2 = [(r[-5][-1], r[-4][-1][-1], i, 0, 0) for i in r[-3][1]]
#                    cc2 = [(r[-5][-1], i, 0, 0, 0) for i in r[-4][1]]
#                    rr = xx + yy + zz + cc + vv + xx2 + yy2 + zz2 + cc2
#    return rr

def get_route_info_database(*args, start_time=None, end_time=None, deep=4, **kvargs):
    dx = kvargs
    if 'start_time' in dx.keys():
        del dx['start_time']
    if 'end_time' in dx.keys():
        del dx['end_time']
    if 'deep' in dx.keys():
        del dx['deep']
    x = []
    t = []
    target = ['route', 'base']
    if start_time and end_time:
        start_time = get_time_tuple(start_time)
        end_time = get_time_tuple(end_time)
    elif start_time:
        start_time = get_time_tuple(start_time)
        end_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    else:
        start_time = datetime.datetime.now() - datetime.timedelta(days=1) + datetime.timedelta(hours=3)
        end_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    t = get_time_requests(start_time, end_time, deep=deep)
    x.append(dx)
    x.append(t)
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
            y = db_find(dx, target=target, limit=10000)
            for i in y:
                if i not in x:
                    x.append(i)
    else:
        y = db_find(dx, target=target, limit=10000)
        x.append(dx)
        for i in y:
            if i not in x:
                x.append(i)
    return [len(x), x[0], x[-1]]

if __name__ == '__main__':
    start_time = (2017, 1, 20, 22, 23)
    end_time = (2017, 1, 22, 22, 23)
#    print(get_route_info_database(**{'blle':'dsfsdf', 'flll':'sfadsf', 'start_time': (2033, 5, 12, 23, 56), 'end_time':None}))

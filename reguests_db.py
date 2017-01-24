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
    return tuple(time_str.split(sep='_'))

def get_time_requests(start_time, end_time):
    r = []
    n = 0
    try:
        s = datetime.datetime(*start_time)
    except:
        s = start_time
    try:
        e = datetime.datetime(*end_time)
    except:
        e = end_time
    x = [[int(i), int(j), g] for i, j, g in [(s.year, e.year, 0), (s.month, e.month, 12), (s.day, e.day, 31), (s.hour, e.hour, 60), (s.minute, e.minute, 60)]]
    f = years(*x[0])
    r.append(f)
    if not f[0]:
        return False
    for i in range(0, len(x)):
        try:
            if i+1 <= len(x) + 1:
                if len(years(*x[0])) == 1 and i == 0 or i != 0 and len(f[0]) == 1:
                    f = over(*x[i+1], pre=True)
                else:
                    f = over(*x[i+1])
                if not f[0]:
                    return False
                r.append(f)
        except IndexError:
            pass
    rr = []
    if len(r[-1]) == 1:
        xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
        rr = xx
    else:
        if len(r[-2]) == 1:
            xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
            yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
            xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
            rr = xx + yy + xx2
        else:
            if len(r[-3]) == 1:
                xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
                yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
                zz = [(r[-5][0], r[-4][0][0], i, 0, 0) for i in r[-3][0]]
                xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
                yy2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], i, 0) for i in r[-2][1]]
                rr = xx + yy + zz + xx2 + yy2
            else:
                if len(r[-4]) == 1:
                    xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
                    yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
                    zz = [(r[-5][0], r[-4][0][0], i, 0, 0) for i in r[-3][0]]
                    cc = [(r[-5][0], i, 0, 0, 0) for i in r[-4][0]]
                    xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
                    yy2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], i, 0) for i in r[-2][1]]
                    zz2 = [(r[-5][-1], r[-4][-1][-1], i, 0, 0) for i in r[-3][1]]
                    rr = xx + yy + zz + cc + xx2 + yy2 + zz2
                else:
                    xx = [(r[-5][0], r[-4][0][0], r[-3][0][0], r[-2][0][0], i) for i in r[-1][0]]
                    yy = [(r[-5][0], r[-4][0][0], r[-3][0][0], i, 0) for i in r[-2][0]]
                    zz = [(r[-5][0], r[-4][0][0], i, 0, 0) for i in r[-3][0]]
                    cc = [(r[-5][0], i, 0, 0, 0) for i in r[-4][0]]
                    vv = [(i, 0, 0, 0, 0) for i in r[-5]]
                    xx2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], r[-2][-1][-1], i) for i in r[-1][1]]
                    yy2 = [(r[-5][-1], r[-4][-1][-1], r[-3][-1][-1], i, 0) for i in r[-2][1]]
                    zz2 = [(r[-5][-1], r[-4][-1][-1], i, 0, 0) for i in r[-3][1]]
                    cc2 = [(r[-5][-1], i, 0, 0, 0) for i in r[-4][1]]
                    rr = xx + yy + zz + cc + vv + xx2 + yy2 + zz2 + cc2
    return rr

def get_route_info_database(src_ip=None, dst_ip=None, start_time=None, end_time=None, protocol=None, port=None):
    dx = {'name': 'CONN', 'action': 'close'}
    x = []
    t = []
    target = ['route', 'base']
    if src_ip:
        dx['connsrcip'] = src_ip
    if dst_ip:
        dx['connnewsrcip'] = dst_ip
    if port:
        dx['conndestport'] = port
    if protocol == "ALL_TO_WAN":
        dx['conndestif'] = 'wan1'
    if start_time and end_time:
        start_time = get_time_tuple(start_time)
        end_time = get_time_tuple(end_time)
        t = get_time_requests(start_time, end_time)
    elif start_time:
        start_time = get_time_tuple(start_time)
        end_time = datetime.datetime.now()
    else:
        start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        end_time = datetime.datetime.now()
    t = get_time_requests(start_time, end_time)
    if t:
        for j in t:
            if j[0]:
                dx['year'] = j[0]
            if j[1]:
                dx['month'] = j[1]
            if j[2]:
                dx['day'] = j[2]
            if j[3]:
                dx['hour'] = j[3]
            if j[4]:
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
    return x

if __name__ == '__main__':
    start_time = (2017, 1, 20, 22, 23)
    end_time = (2017, 1, 22, 22, 23)
    print(get_time_requests(start_time,end_time))
    start_time = datetime.datetime.now() - datetime.timedelta(days=2)
    print(start_time)



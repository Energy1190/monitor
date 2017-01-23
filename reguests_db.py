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

def get_time_requests(start_time, end_time):
    r = []
    n = 0
    s = datetime.datetime(*start_time)
    e = datetime.datetime(*end_time)
    x = [[int(i), int(j), g] for i, j, g in [(s.year, e.year, 0), (s.month, e.month, 12), (s.day, e.day, 31), (s.hour, e.hour, 60), (s.minute, e.minute, 60)]]
    f = years(*x[0])
    r.append(f)
    if not f[0]:
        return False
    for i in range(0, len(x)):
        try:
            if i+1 <= len(x) + 1:
                if len(years(*x[0])) == 1 and i == 0 or i != 0 and len(f) == 1:
                    f = over(*x[i+1], pre=True)
                else:
                    f = over(*x[i+1])
                if not f[0]:
                    return False
                r.append(f)
        except IndexError:
            pass
    return r

def get_route_info_database(src_ip=None, dst_ip=None, start_time=None, end_time=None, protocol=None, port=None):
    dx = {'name': 'CONN', 'action': 'close'}
    x = []
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
        pass
    elif start_time:
        pass
    y = db_find(dx, target=target, limit=10000)
    for i in y:
        if i not in x:
            x.append(i)
    return x

if __name__ == '__main__':
    start_time = (2017, 1, 20, 22, 24)
    end_time = (2018, 1, 20, 22, 23)
    print(get_time_requests(start_time,end_time))



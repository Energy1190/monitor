from db import db_find

def get_route_info_database(src_ip=None, dst_ip=None, start_time=None, end_time=None, protocol=None):
    x = []
    x.append(protocol)
    x.append(type(protocol))
    target = ['route', 'base']
    if protocol:
        y = db_find(dict_db={'connipproto': 'UDP'}, target=target, limit=10000)
        for i in y:
            x.append(i)
    return x

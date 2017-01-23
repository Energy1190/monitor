from db import db_find

def get_route_info_database(src_ip=None, dst_ip=None, start_time=None, end_time=None, protocol='All'):
    x = []
    target = ['route', 'base']
    if protocol == 'UDP':
        y = db_find(dict_db={'connipproto': 'UDP'}, target=target, limit=10000)
        x = [ i for i in y ]
    return x

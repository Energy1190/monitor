from requests_s import Route, Vals, get_database_incoming
from logmodule import logger

def main(target, out_target):
    try:
        t = get_database_incoming(target, status=None)
        if t:
            x = Route(t, target=target)
            y = x.set_dict()
            if y:
                Vals(y, target=['system', 'vals'])
                x.set(x.dicts, target=out_target)
                x.delete(t,target=target)
                return True
            else:
                x.delete(t,target=target)
                return False
    except Exception as err:
        logger.error('Error processing incoming log: {0}'.format(str(err)))

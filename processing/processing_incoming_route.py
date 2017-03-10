from traceback import format_exc
from requests_s import get_database_incoming
from classes.route import Route
from logmodule import logger

def main(target, out_target):
    try:
        t = get_database_incoming(target, status=None)
        if t:
            x = Route(t, target=target)
            if x.set_dict():
                x.set(x.dicts, target=out_target)
                x.delete(t,target=target)
                return True
            else:
                x.delete(t,target=target)
                return False
    except Exception as err:
        logger.error('Error processing incoming log: {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

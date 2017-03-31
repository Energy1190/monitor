from traceback import format_exc
from classes.route import Route
from classes.vals import Vals
from requests_s import get_database_incoming
from system.logmodule import logger


def main(target, out_target, vals):
    try:
        t = get_database_incoming(target, status=None)
        if t:
            x = Route(t, target=target)
            if x.set_dict():
                x.set(x.dicts, target=out_target)
                vals.check(x.dicts)
                x.delete(t,target=target)
                return True
            else:
                x.delete(t,target=target)
                return False
    except Exception as err:
        logger.error('Error processing incoming log: {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))

from traceback import format_exc
from classes.route import Vals
from db import db_find
from logmodule import logger

def main(target, target_system):
    try:
        for i in db_find(target=target, limit=100):
            Vals(i, target=target_system)
    except Exception as err:
        logger.error('Fail get vals {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))
from traceback import format_exc
from classes.db_mongo import Database
from classes.vals import Vals
from system.logmodule import logger

def main(target, target_system):
    try:
        for i in Database(target=target, limit=100).find():
            Vals(i, target=target_system)
    except Exception as err:
        logger.error('Fail get vals {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))
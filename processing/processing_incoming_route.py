import os
import gc
import logging
from traceback import format_exc
from classes.base import Route
from classes.db_mongo import Database

def main(target, out_target, vals, logging=logging):
    def get_database_incoming(target, status=None):
        x = Database(target=target)
        if status:
            x.change(fild='Status', fild_var=status)
        return [dict(x.get()), x.count(x.find)]

    def object_operation(object, object_class, target):
        x = object_class(output=open(os.devnull, 'w'))
        x.set_storage(type='mongoDB', target=target)
        x.set_main(object)
        x.check_collection('mongoDB', target)
        x.set_object()

    incoming, count = get_database_incoming(target, status=None)
    try:
        if incoming:
            object_operation(incoming, Route, out_target)
    except Exception as err:
        logging.error('Can not process incoming object')
        logging.error(str(format_exc()))

    try:
        Database(target=target, dicts=incoming).delete()
    except:
        logging.error('Can not delete incoming object')
        logging.error(str(incoming))
        logging.error(str(format_exc()))

    if count:
        logging.info('In the target database {0}, there are still {1} records requiring processing'.format(str(target), str(count)))

import gc
import logging
from traceback import format_exc
from classes.base import Route
from classes.db_mongo import Database

def main(target, out_target, vals):
    def get_database_incoming(target, status=None):
        x = Database(target=target)
        if status:
            x.change(fild='Status', fild_var=status)
        return [x.get(), x.count(x.find)]

    def object_operation(object, object_class, target):
        x = object_class()
        x.set_storage(type='mongoDB', target=target)
        x.set_main(object)
        x.set_object()

    incoming, count = get_database_incoming(target, status=None)
    try:
        if incoming:
            object_operation(incoming, Route, out_target)
    except Exception as err:
        logging.error('Can not process incoming object')
        logging.error(str(format_exc()))

    if count >=1:
        main(target, out_target, vals)
    gc.collect()

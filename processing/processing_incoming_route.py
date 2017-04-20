import os
import sys
import logging
from traceback import format_exc
from classes.base import Route
from classes.db_mongo import Database

def main(target, out_target, vals, output=sys.stdout, error=sys.stderr):
    def get_database_incoming(target, status=None):
        x = Database(target=target)
        if status:
            x.change(fild='Status', fild_var=status)
        return [x.find(), x.count(x.find)]

    def object_operation(object, object_class, target):
        x = object_class(output=open(os.devnull, 'w'))
        x.set_storage(type='mongoDB', target=target)
        x.set_main(object)
        x.check_collection('mongoDB', target)
        x.set_object()

    i = 'Incoming object'
    incoming, count = get_database_incoming(target, status=None)
    print('Processing of {0} incoming requests from the {1} collection starts'.format(str(count), str(target)), file=output)

    try:
        if incoming:
            for i in incoming:
                object_operation(i, Route, out_target)
    except Exception as err:
        print('Can not process incoming object', file=error)
        print(str(i), file=error)
        print(str(format_exc()), file=error)

    try:
        if incoming:
            for i in incoming:
                Database(target=target, dicts=i).delete()
    except:
        print('Can not delete incoming object', file=error)
        print(str(incoming), file=error)
        print(str(format_exc()), file=error)


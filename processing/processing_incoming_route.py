import os
import sys
import logging
from traceback import format_exc
from classes.base import Route
from classes.db_mongo import Database

c = [0, 0]
def counter():
    global c
    c[0] += 1
    if c > 1000000:
        c[0] = 0
        c[1] += 1
    return c

def main(target, out_target, vals, output=sys.stdout, error=sys.stderr):
    def get_database_incoming(target, status=None):
        x = Database(target=target)
        if status:
            x.change(fild='Status', fild_var=status)
        return [x.get(), x.count(x.find)]

    def object_operation(object, object_class, target):
        x = object_class(output=open(os.devnull, 'w'))
        x.set_storage(type='mongoDB', target=target)
        x.set_main(object)
        x.check_collection('mongoDB', target)
        x.set_object()

    incoming, count = get_database_incoming(target, status=None)
    print('Incoming object detect: {0}'.format(str(incoming)), file=output)
    print('Counts: {0}'.format(str(counter())))
    
    try:
        if incoming:
            object_operation(incoming, Route, out_target)
    except Exception as err:
        print('Can not process incoming object', file=error)
        print(str(format_exc()), file=error)

    try:
        if incoming:
            Database(target=target, dicts=incoming).delete()
    except:
        print('Can not delete incoming object', file=error)
        print(str(incoming), file=error)
        print(str(format_exc()), file=error)

    if count:
        print('In the target database {0}, there are still {1} records requiring processing'.format(str(target), str(count)), file=output)

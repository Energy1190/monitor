import sys
import pytz
import datetime
from traceback import format_exc
from classes.base import Base, Comp, User, Dhcp
from classes.db_mongo import Database
from classes.crypts import Crypt
from system.system import error_log_write

def main(target, out_target_users, out_target_comps, out_dhcp_target, output=sys.stdout, error=sys.stderr):
    def get_database_incoming(target, status=None):
        x = Database(target=target)
        if status:
            x.change(fild='Status', fild_var=status)
        return [x.get(), x.count(x.find)]

    def object_operation(object, object_class, target, name):
        x = object_class()
        x.set_storage(type='mongoDB', target=target)
        y = (x.set_main(object) or x.generate_main_list(object))
        if type(y) == list:
            x.generate_from_list(y, 'dhcp', time=datetime.datetime.now(pytz.timezone('Europe/Moscow')))
        else:
            x.check_object(name)
            if x.exist:
                x.update_object()
            else:
                x.set_object()

    def decrypt(target, key):
        x = Crypt()
        x.set_key(key)
        return x.remove_end(target)

    print('---'*20, file=output)
    print('A new inbound object was detected', file=output)
    incoming, count = get_database_incoming(target, status='New')
    original = incoming
    try:
        if incoming:
            d = incoming.get('Targets')
            x = decrypt(incoming.get('Body'), incoming.get('Key'))
            if x:
                incoming = x
            else:
                print('The object was not decrypted', file=error)
            print('Object contains the following keys: {0}'.format(str(list(incoming))), file=output)
            print('Assign an object - {0}'.format(str(d)), file=output)
            if d == 'report':
                if int(incoming['Version']) > 2:
                    object_operation(incoming, Comp, out_target_comps, incoming['Userinfo']['Computername'])
                object_operation(incoming, User, out_target_users, incoming['Userinfo']['Username'])
            elif d == 'dhcp':
                object_operation(incoming.get("Dhcpinfo"), Dhcp, out_dhcp_target, None)
            else:
                print('The incoming object can not be processed, information about it is placed in the log file', file=error)
                error_log_write(str(original), err='Can not be processed')
    except Exception as err:
        print('There were errors processing the incoming object', file=error)
        print(str(incoming), file=error)
        print(str(format_exc()), file=error)
        error_log_write(str(original), err='Errors occurred')

    Database(target=target, dicts=original).delete()
    print('The incoming object was processed and deleted', file=output)
    if count >= 1:
        main(target, out_target_users, out_target_comps, out_dhcp_target)

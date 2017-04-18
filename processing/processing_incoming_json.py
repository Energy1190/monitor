import pytz
import datetime
import logging
from traceback import format_exc
from classes.base import Base, Comp, User, Dhcp
from classes.db_mongo import Database
from classes.crypts import Crypt
from system.system import error_log_write

def main(target, out_target_users, out_target_comps, out_dhcp_target):
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

    logging.info('---'*20)
    logging.info('A new inbound object was detected')
    incoming, count = get_database_incoming(target, status='New')
    original = incoming
    try:
        if incoming:
            d = incoming.get('Targets')
            x = Crypt().remove_end(incoming.get('Body'))
            if x:
                incoming = x
            if d == 'report':
                if int(incoming['Version']) > 2:
                    object_operation(incoming, Comp, out_target_comps, incoming['Userinfo']['Computername'])
                object_operation(incoming, User, out_target_users, incoming['Userinfo']['Username'])
            elif d == 'dhcp':
                object_operation(incoming.get("Dhcpinfo"), Dhcp, out_dhcp_target, None)
            else:
                logging.error('The incoming object can not be processed, information about it is placed in the log file')
                error_log_write(str(original), err='Can not be processed')
    except Exception as err:
        logging.error('There were errors processing the incoming object')
        logging.error(str(format_exc()))
        error_log_write(str(original), err='Errors occurred')

    Database(target=target, dicts=original).delete()
    logging.info('The incoming object was processed and deleted')
    if count >= 1:
        main(target, out_target_users, out_target_comps, out_dhcp_target)

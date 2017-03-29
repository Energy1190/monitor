from traceback import format_exc
from classes.base import Base
from classes.clients import Comp, User, Dhcp
from classes.db_mongo import Database
from classes.vals import Iptable
from system.system import error_log_write
from system.logmodule import logger


def get_database_incoming(target, status=None):
    x = Database(target=target)
    if status:
        x.change(fild='Status', fild_var=status)
    return [x.get(), x.count(x.find)]

def decrypt(crypt):
    if 'Crypt' in list(crypt) and crypt['Crypt'] == 'true':
        def decrypt_str(crypt):
            d = crypt.get('Targets')
            return [Base(crypt).remove_end(crypt.get('Body')), d]
        return decrypt_str(crypt)
    else:
        return [crypt, 'old']

def main(target, out_target_users, out_target_comps, dhcp_target):
    t = get_database_incoming(target, status='New')
    count = 0
    try:
        incoming, count = t
        if incoming:
            incoming, d = decrypt(incoming)
            if d == 'report':
                if int(incoming['Version']) > 2:
                    x = Comp(incoming, target=out_target_comps)
                    y = x.get_dsttrg(incoming['Userinfo']['Computername'], 'computername')
                    if y:
                        x.check_dict(y)
                        x.update(dsttrg=y)
                    else:
                        x.set(x.dicts)
                x = User(incoming, target=out_target_users)
                y = x.get_dsttrg(incoming['Userinfo']['Username'], 'username')
                error_log_write(str(x), err=str('Check class'))
                error_log_write(str(incoming['Userinfo']['Username']), err=str('Check class'))
                error_log_write(str(y), err=str('Check class'))
                if y:
                    error_log_write(str(y), err=str('Check base'))
                    x.check_dict(y)
                    x.update(dsttrg=y)
                else:
                    x.set(x.dicts)
                x.delete(t[0], target=target)
            elif d == 'dhcp':
                    x = Dhcp(t, target=dhcp_target)
                    x.set_dict()
                    for i in x.dicts['dhcpinfo']:
                        y = x.get_dsttrg(i['name'], 'name')
                        if y:
                            x.update(srctrg=i, dsttrg=y)
                        else:
                            x.set(i)
                    x.delete(t[0], target=target)
            else:
                logger.error('Unidentified JSON detect. Delete.')
                logger.error('Object: {0}'.format(str(t[0])))
                Database(dicts=t[0], target=target).delete()
    except Exception as err:
        logger.error('Error processing incoming json: {0}'.format(str(err)))
        logger.error('Trace: {0}'.format(str(format_exc())))
        Database(dicts=t[0], target=target).delete()
    if count > 1:
        main(target, out_target_users, out_target_comps, dhcp_target)
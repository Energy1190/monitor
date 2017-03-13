from traceback import format_exc
from classes.clients import Comp, User, Dhcp
from classes.db_mongo import Database
from requests_s import get_database_incoming, decrypt_str
from system import error_log_write, send_mail
from logmodule import logger

def main(target, out_target_users, out_target_comps, dhcp_target):
    t = get_database_incoming(target, status='New')
    incoming = t
    if t:
        try:
            if 'Crypt' in list(t) and t['Crypt'] == 'true':
                t, d = decrypt_str(t)
                error_log_write(str(t + d), err='Check')
            if 'Version' in list(t) or d == 'report':
                if int(t['Version']) > 2:
                    x = Comp(t, target=out_target_comps)
                    y = x.get_dsttrg(t['Userinfo']['Computername'], 'computername')
                    if y:
                        x.check_dict(y)
                        x.update(dsttrg=y)
                    else:
                        x.set(x.dicts)
                x = User(t, target=out_target_users)
                y = x.get_dsttrg(t['Userinfo']['Username'], 'username')
                if y:
                    x.check_dict(y)
                    x.update(dsttrg=y)
                else:
                    x.set(x.dicts)
                x.delete(t, target=target)
            elif d == 'dhcp':
                    x = Dhcp(t, target=dhcp_target)
                    x.set_dict()
                    for i in x.dicts['dhcpinfo']:
                        y = x.get_dsttrg(i['name'], 'name')
                        if y:
                            if str(y['ip']) != str(i['ip']):
                                x.update(srctrg=i, dsttrg=y)
                        else:
                            x.set(i)
                    x.delete(t, target=target)
        except Exception as err:
            logger.error('Error processing incoming json: {0}'.format(str(err)))
            logger.error('Trace: {0}'.format(str(format_exc())))
            Database(dicts=incoming, target=target).delete()
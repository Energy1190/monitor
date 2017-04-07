import datetime
from system.configuration import get_val
from system.system import send_mail
from requests_s import check_base
from classes.vals import Iptable
from classes.db_mongo import Database

def get_iplist(target=None, names=None, users=None):
    Iptable(target=target, names=names, users=users)

def checks(l):
    for i in l:
        check_base(i)

def sending_mails():
    xl = []

    def get_check_list(name):
        target = get_val(name)
        return [ i['name'] for i in target]

    def send_text(xl):
        x = ["Can't connect to server {0} \n".format(i) for i in xl if i != 'start' ]
        if 'start' in xl:
            x.append("Daemon start work.")
            Database(target=['systems', 'watch'], dicts={'name': 'start'}).update({'name': 'start', 'status': True})
        return ' '.join(x)

    target = get_check_list('[Checks]')
    target.append('start')
    for i in target:
        x = Database(target=['systems', 'watch'], dicts={'name': i}).get()
        if x and not x['status']:
            xl.append(i)
    send_mail(send_text(xl), subject='Daemon status')

def main():
    time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
    target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                  time_now.timetuple()[1],
                                                  time_now.timetuple()[2])
    get_iplist(target=['systems', 'iptables'], names=['clients', 'dhcp'], users=['clients', 'users'])
    checks([['clients', 'comps'], ['clients', 'users'], ['clients', 'dhcp']])
    sending_mails()

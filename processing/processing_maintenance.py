import sys
import datetime
from system.configuration import get_val
from system.system import send_mail
from system.requestus import check_base
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

    def send_text(xl, check=None):
        x = ["Can't connect to server {0} \n".format(i) for i in xl if i != 'start' or type(i) != tuple]
        [x.append("\tFail check {1} on server {0} \n".format(i[0], i[1])) for i in xl if type(i) == tuple]
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
        elif x and x.get('checks'):
            for j in x.get('checks'):
                if not x.get('checks')[j]:
                    xl.append((i, j))
    t = send_text(xl)
    if t:
        print('Sending mail', file=sys.stdout)
        send_mail(t, subject='Daemon status')

def clear_collection(collection_now):
    t_list = []
    t_now = datetime.datetime(*map(int, collection_now.split(sep='-')[1:])) + datetime.timedelta(days=1)
    for i in range(32):
        t_list.append(t_now.timetuple()[:3])
        t_now = t_now - datetime.timedelta(days=1)
    x = [{tuple(map(int, i.split(sep='-')[1:])): t_list.count(tuple(map(int, i.split(sep='-')[1:])))}
          for i in Database(target=['route']).get_collections_names() if 'base' in str(i)]
    for i in x:
        for j in i:
            if not i[j]:
                print('Delete collection {0}'.format(str('base-' + '-'.join(list(map(str, j))))))
                base = Database(target=['route', str('base-' + '-'.join(list(map(str, j))))])
                print(base.delete_all())
                print(base.drop())

def main():
    time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
    target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                  time_now.timetuple()[1],
                                                  time_now.timetuple()[2])
    get_iplist(target=['systems', 'iptables'], names=['clients', 'dhcp'], users=['clients', 'users'])
    checks([['clients', 'comps'], ['clients', 'users'], ['clients', 'dhcp']])
    sending_mails()
    clear_collection(target_collection)

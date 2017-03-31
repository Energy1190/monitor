import datetime
from requests_s import check_base
from classes.vals import Iptable
from processing.processing_get_vals import main as processing_get_vals

def get_iplist(target=None, names=None, users=None):
    Iptable(target=target, names=names, users=users)

def checks(l):
    for i in l:
        check_base(i)

def main():
    time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
    target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                  time_now.timetuple()[1],
                                                  time_now.timetuple()[2])
    get_iplist(target=['systems', 'iptables'], names=['clients', 'dhcp'], users=['clients', 'users'])
    checks([['clients', 'comps'], ['clients', 'users'], ['clients', 'dhcp']])

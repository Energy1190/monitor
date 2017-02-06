#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import os
import requests
import time
import threading
from configuration import get_val
from system import send_mail

def get_db_connect(http, flag='url'):
    try:
        r = requests.get(url=http)
        if r.status_code == 200:
            if flag == 'db':
                if dict(r.json())['result']:
                    return True
                else:
                    return False
            else:
                return True
        elif flag == 'forbidden' and r.status_code == 403:
            return True
        else:
            return False
    except:
        return False

def get_check_list(name):
    target = get_val(name)
    return [{'target': i['name'], 'flag': i['flag']} for i in target ]

def checks_server(i, flag=None):
    if flag == 'ping':
        x = os.system("ping -c 1 " + i['target'])
    else:
        x = get_db_connect(i['target'], flag=i['flag'])
    if not x:
        time.sleep(300)
        if not x:
            send_mail('Fail connect to {0} as {1}'.format(i['target'], i['flag']), host=i['target'])

def main():
    send_mail(str('Start work. Checks: {0}'.format([str(i['target'] + ' as ' + i['flag']) for i in get_check_list()])),
              subject='Daemon start work')
    try:
        while True:
            target = get_check_list('[Checks]')
            for i in target:
                threading.Thread(target=checks_server, args=(i), kwargs={'flag' : i['flag']}).start()
            time.sleep(3600)
    finally:
        send_mail('End work')

if __name__ == '__main__':
#    print(get_check_list())
    pass
    file = open('ss.txt', 'a+')
    file.write('Hello')

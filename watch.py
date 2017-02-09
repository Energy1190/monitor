#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import os
import requests
import time
import multiprocessing
from traceback import format_exc
from configuration import get_val
from system import send_mail, error_proc

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
    try:
        target = get_check_list('[Checks]')
        send_mail(str('Start work. Checks: {0}'.format([str(i['target'] + ' as ' + i['flag']) for i in get_check_list('[Checks]')])),
                  subject='Daemon start work')
        while True:
            n = 0
            for i in target:
                try:
                    n += 1
                    name = "watch-" + str(n)
                    proc = multiprocessing.Process(name=name, target=checks_server, args=(i), kwargs={'flag' : i['flag']})
                    proc.start()
                except Exception as err:
                    error_proc(body=format_exc(), log=True, mail=True, subject='Local error in watch-daemon', error=err)
            time.sleep(3600)
    finally:
        send_mail('Daemon end work', subject='Daemon end work')

if __name__ == '__main__':
#    print(get_check_list())
    pass
    file = open('ss.txt', 'a+')
    file.write('Hello')

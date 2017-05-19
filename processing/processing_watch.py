#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import os
import sys
import threading
import time
import requests
from traceback import format_exc
from system.configuration import get_val
from system.system import send_mail
from system.logmodule import logger
from classes.db_mongo import Database

def check_db(t, dicts=None):
    x = Database(target=['systems', 'watch'], dicts=dicts)
    if x.get():
        x.update(t)
    else:
        x.set(t)

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
    [i.setdefault('target', i['name']) for i in target]
    return target

def check_smb_v1(target, result):
    from smb import smb_structs
    from smb import SMBConnection

    if target.get('user') and target.get('password') and target.get('domain_name') and target.get('domain'):
        print('Start SMBv1 check', file=sys.stdout)
        try:
            smb_structs.SUPPORT_SMB2 = target.get('SMBv1')
            x = SMBConnection.SMBConnection(target.get('user'), target.get('password'), 'testus', target.get('domain_name'), domain=target.get('domain'), is_direct_tcp=True)
            r = x.connect(target.get('target'), port=445, timeout=60)
            print('SMBv1 check end with out error', file=sys.stdout)
        except:
            print('SMBv1 check end error connection', file=sys.stdout)
            r = False
    else:
        print('missing parameters', file=sys.stdout)
        r = not result

    print(result, r, file=sys.stdout)
    if result == r:
        return True
    else:
        return False

def checks_server(i, flag=None):
    logger.debug('Launched check to {0} as {1}'.format(i['target'], i['flag']))
    checks = {}
    status = True
    if flag == 'ping':
        x = os.system("ping -c 1 " + i['target'] + " 1>/dev/null")
        if x:
            time.sleep(300)
            if x:
                status = False
    else:
        x = get_db_connect(i['target'], flag=i['flag'])
        if not x:
            time.sleep(300)
            if not x:
                status = False
    if 'SMBv1' in i:
        checks['SMBv1'] = check_smb_v1(i, i['SMBv1'])
    check_db({'name': i['target'], 'status': status, 'checks': checks}, dicts={'name': i['target']})

def main():
    logger.info('begin to follow...')
    try:
        logger.info('Start watch to servers')
        target = get_check_list('[Checks]')
        check_db({'name': 'start', 'status': False}, dicts={'name': 'start'})
        while True:
            n = 0
            for i in target:
                try:
                    n += 1
                    name = "watch-" + str(n)
                    threading.Thread(name=name, target=checks_server, args=[i], kwargs={'flag' : i['flag']}).start()
                except Exception as err:
                    logger.error('Local error in watch-daemon')
                    logger.error(str(format_exc()))
            time.sleep(3600)
    finally:
        logger.warning('Ranger finished work, this should not have happened')
        send_mail('Daemon end work', subject='Daemon end work')

if __name__ == '__main__':
    pass
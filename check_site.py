#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import requests
import smtplib
import time
from email.mime.text import MIMEText
from get_config import get_section

def send_mail(text, host='site'):
    msg = MIMEText(text)
    msg['Subject'] = 'Can not connect to {0}'.format(host)
    msg['From'] = 'daemon-check-site@intersoftlab.ru'
    msg['To'] = 'energyneo0@gmail.com'
    s = smtplib.SMTP('172.16.0.4')
    s.send_message(msg)
    s.quit()

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

def main():
    print(get_section('[Check HTTP]'))
    send_mail('Start work')
    try:
        while True:
            target = get_section('[Check HTTP]')
            for i in range(0, len(target)):
                if target[i][0:4] == 'http':
                    if not get_db_connect(target[i], flag=target[i+1]):
                        time.sleep(300)
                        if not get_db_connect(target[i], flag=target[i+1]):
                            send_mail('Fail connect to {0} as {1}'.format(target[i], target[i+1]), host=target[i])
            time.sleep(3600)
    finally:
        send_mail('End work')

if __name__ == '__main__':
    print('https'[0:3])

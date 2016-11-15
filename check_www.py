#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import requests
import smtplib
import time
from email.mime.text import MIMEText

def send_mail(text):
    msg = MIMEText(text)
    msg['Subject'] = 'Can not connect to www'
    msg['From'] = 'daemon-www-site@intersoftlab.ru'
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
        else:
            return False
    except:
        return False

def main():
    while True:
        if not get_db_connect('http://iso.ru'):
            send_mail('Fail main connect to www.iso.ru')
        if not get_db_connect('http://iso.ru/system/ajax/documents.php?_path=main.root.ru.press-center.news&limit=10&offset=10&_type=296&_sort=-_publish_time',flag='db'):
            send_mail('Fail db connect to www.iso.ru')
        time.sleep(28800)

if __name__ == '__main__':
    send_mail('Start work')
    main()
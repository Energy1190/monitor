#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import requests
import smtplib
import time
from email.mime.text import MIMEText

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
    send_mail('Start work')
    try:
        while True:
            if not get_db_connect('http://iso.ru'):
                time.sleep(300)
                if not get_db_connect('http://iso.ru'):
                    send_mail('Fail main connect to www.iso.ru', host='www.iso.ru')
            if not get_db_connect('http://iso.ru/system/ajax/documents.php?_path=main.root.ru.press-center.news&limit=10&offset=10&_type=296&_sort=-_publish_time',flag='db'):
                time.sleep(300)
                if not get_db_connect('http://iso.ru/system/ajax/documents.php?_path=main.root.ru.press-center.news&limit=10&offset=10&_type=296&_sort=-_publish_time',flag='db'):
                    send_mail('Fail db connect to www.iso.ru', host='www.iso.ru')
            if not get_db_connect('https://subversion.iso.ru', flag='forbidden'):
                time.sleep(300)
                if not get_db_connect('http://subversion.iso.ru', flag='forbidden'):
                    send_mail('Fail main connect to subversion.iso.ru', host='subversion.iso.ru')
            if not get_db_connect('https://trackstudio.iso.ru'):
                time.sleep(300)
                if not get_db_connect('https://trackstudio.iso.ru'):
                    send_mail('Fail main connect to trackstudio.iso.ru', host='trackstudio.iso.ru')
            time.sleep(3600)
    finally:
        send_mail('End work')

if __name__ == '__main__':
    print(get_db_connect('https://subversion.iso.ru', flag='forbidden'))

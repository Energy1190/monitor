import datetime
import os
import smtplib
import time
import threading
from classes.vals import Count
from email.mime.text import MIMEText
from system.configuration import get_val
from system.logmodule import logger

error_c = 0
log_lock = False
time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
time_now_tuple = time_now.timetuple()[0:4]
target_collection ='base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                             time_now.timetuple()[1],
                                             time_now.timetuple()[2])

def counter(class_name, operation):
    def class_count(func):
        def wraper(*args, **kwargs):
            x = Count()
            x.set_count(class_name, operation)
            return func(*args, **kwargs)
        return wraper()

def maintenance(time):
    def main_func(func):
        def wraper(*args, **kwargs):
            threading.Thread(target=flush_counts,args=(time)).start()
            return func(*args, **kwargs)
        return wraper()

def flush_counts(time):
    while True:
        x = Count()
        x.update_base()
        time.sleep(time)

def watch_pid():
    pid = os.getpid()
    if not os.path.exists('pid.num'):
        f = open('pid.num', 'w+')
        f.write(str(pid) + '\n')
        f.close()
        print('Program PID is {0}'.format(str(pid)))
    else:
        print('Detect duplicate program. PID - {0}'.format(str(pid)))

def write_pid(pid):
    if os.path.exists('pid.num'):
        f = open('pid.num', 'a+')
        f.write(str(pid) + '\n')
        f.close()

def get_pid(pid, alls=False):
    if os.path.exists('pid.num'):
        f = open('pid.num', 'r')
        try:
            if alls:
                return [i.replace('\n', '') for i in f]
            else:
                for i in f:
                    if i.replace('\n', '') == str(pid):
                        return True
                    else:
                        return False
        finally:
            f.close()

def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        logger.debug('Subprocess - pid {0} not detect. Pid delete from list'.format(str(pid)))
        return False
    else:
        return True

def remove_pid(pid):
    if os.path.exists('pid.num'):
        r = get_pid(0, alls=True)
        if str(pid) in r:
            r.remove(str(pid))
        with open('pid.num', 'w+') as f:
            for i in r:
                f.write(str(i + '\n'))
            f.close()

def detect_fail_pid():
    while True:
        if os.path.exists('pid.num'):
            for i in get_pid(0, alls=True):
                if not check_pid(int(i)):
                    remove_pid(i)
        time.sleep(3400)

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def detect_crit():
    logger.info('Start watch to CRITICAL error')
    err = []
    e = False
    mess = str(' - ')
    while True:
        if os.path.exists('logging.log'):
            for i in open('logging.log', 'r'):
                i = str(i)
                if '- CRITICAL -' in i and i not in err:
                    err.append(i)
                    mess += i + '\n'
                    e = True
                elif '- CRITICAL -' not in i and e:
                    if 'INFO' in i or 'ERROR' in i or 'DEBUG' in i or 'WARNING' in i:
                        send_mail(mess, subject='CRITICAL error')
                        mess = str(' - ')
                        e = False
            time.sleep(60)

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def return_nub(x):
    return int(''.join([i for i in x if isfloat(i)]))

def error_log_write(t, err=None):
    global error_c
    error_c += 1
    if not os.path.exists('error.log'):
        file = open('error.log', 'w+')
    else:
        file = open('error.log', 'a+')
    file.write('Error № {0} \n'.format(error_c))
    file.write('Error time {0} \n'.format(datetime.datetime.now() + datetime.timedelta(hours=3)))
    if err and t:
        try:
            if len(t) > 500:
                t = t[0:499] + '\n...part of the text omitted...\n' + t[-500:] + '\n'
        except TypeError:
            pass
        file.write('Error string {0} \n'.format(t))
        file.write('Trace: \n')
        file.write(str(err))
    elif t:
        try:
            if len(t) > 500:
                t = t[0:499] + '\n...part of the text omitted...\n' + t[-500:] + '\n'
        except TypeError:
            pass
        file.write('Error string {0} \n'.format(t))
    else:
        file.write('Empty error')
    file.write('\n \n')
    file.write('--'*10)
    file.write('\n \n')
    file.close()

def error_proc(**kwargs):
    if kwargs.get('body'):
        if kwargs.get('log'):
            error_log_write(kwargs.get('body'), err=kwargs.get('error'))
        if kwargs.get('mail'):
            send_mail(kwargs.get('body'), subject=kwargs.get('subject'))

def send_mail(text, host='site', subject=None):
    r = []
    for i in get_val('[Mail]'):
        if i not in r:
            r.append(i)
            msg = MIMEText(text)
            if not subject:
                msg['Subject'] = 'Can not connect to {0}'.format(host)
            else:
                msg['Subject'] = subject
            msg['From'] = 'daemon-check-site@intersoftlab.ru'
            msg['To'] = i['name']
            s = smtplib.SMTP(get_val('[Mail server]')[0]['ip'])
            s.send_message(msg)
            s.quit()
            logger.info('Send mail to {0} about subject - {1}. Successful.'.format(i['name'], subject))
    return r

if __name__ == '__main__':
    pass

import os
import smtplib
import datetime
import logging
from email.mime.text import MIMEText
from configuration import get_val

error_c = 0
time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
time_now_tuple = time_now.timetuple()[0:4]
target_collection ='base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                             time_now.timetuple()[1],
                                             time_now.timetuple()[2])
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def return_nub(x):
    return int(''.join([i for i in x if isfloat(i)]))

def consol_log(mess, trace=None, level='info'):
    logging.basicConfig(format='%(asctime)-15s [%(level)s] %(message)s \n %(trace)s', datefmt='%Y.%m.%d %I:%M:%S %p')
    if level == 'info':
        logging.info(str(mess), **{'trace': trace, 'level': level})
    elif level == 'warn':
        logging.warning(str(mess),**{'trace': trace, 'level': level})
    elif level ==  'error':
        logging.error(str(mess), **{'trace': trace, 'level': level})
        error_log_write(mess, trace)
    elif level == 'crit':
        logging.critical(str(mess), **{'trace': trace, 'level': level})
        error_log_write(mess, trace)
        if trace:
            send_mail(str(trace), subject=mess)
    elif level == 'debug':
        logging.debug(str(mess), trace)

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
    else:
        file.write('Received empty response from the base.')
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
    for i in get_val('[Mail]'):
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

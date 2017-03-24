import subprocess
import multiprocessing
import os
import time
import datetime
from webapp import app
from watch import watch_main
from traceback import format_exc
from logmodule import logger
from system import detect_crit, write_pid, get_pid, detect_fail_pid
from requests_s import check_base
from processing.processing_incoming_route import main as processing_incoming_route
from processing.processing_statistics_route import main as processing_statistics_route
from processing.processing_get_vals import main as processing_get_vals
from processing.processing_incoming_json import main as processing_incoming_json

def application():
    app.debug = True
    app.secret_key = 'not-secret-key'
    app.run(port=5000, host='0.0.0.0')

def daemon():
    watch_main()

def critical_detect():
    detect_crit()

def get_vals():
    while True:
        time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
        target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                      time_now.timetuple()[1],
                                                      time_now.timetuple()[2])
        processing_get_vals( ['route', target_collection], ['systems', 'vals'])
        check_base(['clients', 'comps'])
        check_base(['clients', 'users'])
        check_base(['clients', 'dhcp'])
        time.sleep(4000)

def processing_logs():
    try:
        while True:
            time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
            target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                          time_now.timetuple()[1],
                                                          time_now.timetuple()[2])
            processing_incoming_route(['route', 'warn'], ['route', target_collection])
            processing_incoming_route(['route', 'notice'], ['route', target_collection])
            x = processing_incoming_route(['route', 'info'], ['route', target_collection])
            if not x:
                time.sleep(5)
    except Exception as err:
        text = 'Fail router logs work\n' + str(format_exc()) + '\n' + str(err)
        logger.critical(text)

def get_dally_statistics():
    x = False
    try:
        while True:
            if datetime.datetime.now().minute == 0 and not x:
                subproc = multiprocessing.Process(name='get_statistic', target=processing_statistics_route,
                                                  args=[['clients', 'dhcp'],['clients', 'stat']])
                subproc.start()
                write_pid(subproc.pid)
                logger.debug('Start subprocess - pid {0} - dally statistic'.format(subproc.pid))
                x = True
            elif datetime.datetime.now().minute == 1 and x:
                x = False
                time.sleep(3400)
            time.sleep(59)
    except Exception as err:
        text = 'Fail daily statistics work\n' + str(format_exc()) + '\n' + str(err)
        logger.critical(text)


if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc1.start()
    pid = os.getpid()
    if not os.path.exists('pid.num'):
        f = open('pid.num', 'w+')
        f.write(str(pid) + '\n')
        f.close()
    else:
        logger.warning('More than one workflow')
        logger.warning('Process {0} exit!'.format(os.getpid()))
        os._exit(1)
    if get_pid(os.getpid()):
        logger.info(str('--' * 20))
        logger.info('Start program. I begin to run processes')
        logger.debug('Program pid: {0}'.format(str(pid)))
        x = subprocess.getstatusoutput(['/bin/bash', '-c', 'python', '/data/monitor/selftest.py'])[0]
        logger.info('Selftest complete. Exit code: {0}'.format(x))
        proc2 = multiprocessing.Process(name='daemon', target=daemon)
        proc4 = multiprocessing.Process(name='logs', target=processing_logs)
        proc5 = multiprocessing.Process(name='dally', target=get_dally_statistics)
        proc6 = multiprocessing.Process(name='critical', target=critical_detect)
        proc7 = multiprocessing.Process(name='vals', target=get_vals)
        for i in [proc2, proc4, proc5, proc6, proc7]:
            i.start()
            write_pid(i.pid)
        logger.info('All processes started')
    else:
        logger.warning('More than one workflow')
        logger.warning('Process {0} exit!'.format(os.getpid()))
        os._exit(1)
    logger.info('Start detects pid')
    detect_fail_pid()

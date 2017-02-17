import subprocess
import multiprocessing
import os
import time
import datetime
from webapp import app
from watch import watch_main
from traceback import format_exc
from logmodule import logger
from system import detect_crit
from processing import processing_statistics_route
from requests_s import delete_old_reqests, check_base, processing_incoming_route, processing_incoming_json

def application():
    app.debug = True
    app.run(port=5000, host='0.0.0.0')

def daemon():
    watch_main()

def critical_detect():
    detect_crit()

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

def edit_requests():
    try:
        while True:
            processing_incoming_json(['clients', 'json'], ['clients', 'users'], ['clients', 'comps'], ['clients', 'dhcp'])
            check_base(['clients', 'comps'])
            check_base(['clients', 'users'])
            check_base(['clients', 'dhcp'])
            time.sleep(360)
    except Exception as err:
        text = 'Fail JSON work\n' + str(format_exc()) + '\n' + str(err)
        logger.critical(text)

def get_dally_statistics():
    try:
        for i in range(60):
            if datetime.datetime.now().minute == 0:
                while True:
                    for i in range(24):
                        time.sleep(3600)
                        name = "dally-" + str(i)
                        subproc = multiprocessing.Process(name=name, target=processing_statistics_route,
                                                          args=[['clients', 'dhcp'],['clients', 'stat']],
                                                          kwargs={'times' : 'hour'})
                        subproc.start()
                        if (datetime.datetime.now() - datetime.timedelta(hours=3)).hour == 0:
                            name = 'dally-full'
                            subprocday = multiprocessing.Process(name=name, target=processing_statistics_route,
                                                              args=[['clients', 'dhcp'], ['clients', 'stat']],
                                                              kwargs={'times': 'day'})
                            subprocday.start()
            time.sleep(60)
    except Exception as err:
        text = 'Fail daily statistics work\n' + str(format_exc()) + '\n' + str(err)
        logger.critical(text)


if __name__ == '__main__':
    logger.info(str('--' * 20))
    logger.info('Start program. I begin to run processes')
    if not subprocess.getstatusoutput(['/bin/bash', '-c', 'python', '/data/monitor/selftest.py'])[0]:
        multiprocessing.Process(name='app', target=application).start()
        multiprocessing.Process(name='daemon', target=daemon).start()
        multiprocessing.Process(name='editor', target=edit_requests).start()
        multiprocessing.Process(name='logs', target=processing_logs).start()
        multiprocessing.Process(name='dally', target=get_dally_statistics).start()
        multiprocessing.Process(name='critical', target=critical_detect).start()
        logger.info('All processes started')

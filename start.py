import multiprocessing
import time
import datetime
import threading
from webapp import app
from watch import main
from traceback import format_exc
from system import target_collection, error_log_write, send_mail, error_c, time_now
from processing import processing_statistics_route
from requests_s import delete_old_reqests, check_base, processing_incoming_route, processing_incoming_json

def application():
    app.debug = True
    app.run(port=5000, host='0.0.0.0')

def daemon():
    try:
        main()
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail daemon watch\n' + str(format_exc()) + '\n' + str(err)
        send_mail(text, subject='Fail daemon works')

def processing_logs():
    try:
        while True:
            processing_incoming_route(['route', 'warn'], ['route', target_collection])
            processing_incoming_route(['route', 'notice'], ['route', target_collection])
            if not processing_incoming_route(['route', 'info'], ['route', target_collection]):
                time.sleep(5)
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail router logs work\n' + str(format_exc()) + '\n' + str(err)
        send_mail(text, subject='Fail logs works')

def edit_requests():
    try:
        while True:
            processing_incoming_json(['clients', 'json'], ['clients', 'users'], ['clients', 'comps'], ['clients', 'dhcp'])
            check_base(['clients', 'comps'])
            check_base(['clients', 'users'])
            check_base(['clients', 'dhcp'])
            time.sleep(360)
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail JSON work\n' + str(format_exc()) + '\n' + str(err)
        send_mail(text, subject='Fail JSON works')

def get_dally_statistics():
    try:
        for i in range(60):
            if datetime.datetime.now().minute == 0:
                while True:
                    for i in range(24):
                        time.sleep(3600)
                        name = "dally-" + str(i)
                        subproc = multiprocessing.Process(name=name, target=processing_statistics_route,
                                                          args=(['clients', 'dhcp'],['clients', 'stat']),
                                                          kwargs={'times' : 'hour'}).start()
                        subproc.start()
                        if time_now.hour == 0:
                            name = 'dally-full'
                            subproc = multiprocessing.Process(name=name, target=processing_statistics_route,
                                                              args=(['clients', 'dhcp'], ['clients', 'stat']),
                                                              kwargs={'times': 'day'}).start()
                            subproc.start()
            time.sleep(60)
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail daily statistics work\n' + str(format_exc()) + '\n' + str(err)
        send_mail(text, subject='Fail statistics works')


if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc2 = multiprocessing.Process(name='daemon', target=daemon)
    proc3 = multiprocessing.Process(name='editor', target=edit_requests)
    proc4 = multiprocessing.Process(name='logs', target=processing_logs)
    proc5 = multiprocessing.Process(name='dally', target=get_dally_statistics)
    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()
    proc5.start()
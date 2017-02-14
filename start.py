import multiprocessing
import time
import datetime
import sys
import logging
from webapp import app
from watch import main
from traceback import format_exc
from system import target_collection, error_log_write, send_mail, error_c, time_now
from processing import processing_statistics_route
from requests_s import delete_old_reqests, check_base, processing_incoming_route, processing_incoming_json

def application(queue):
    app.debug = True
    queue.put(app.run(port=5000, host='0.0.0.0'))

def daemon(queue):
    queue.put(main())

def get_stdout(queue):
    while True:
        if queue.empty():
            time.sleep(5)
        else:
            print(queue.get())

def processing_logs(queue):
    try:
        while True:
            queue.put(processing_incoming_route(['route', 'warn'], ['route', target_collection]))
            queue.put(processing_incoming_route(['route', 'notice'], ['route', target_collection]))
            x = processing_incoming_route(['route', 'info'], ['route', target_collection])
            queue.put(x)
            if not x:
                time.sleep(5)
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail router logs work\n' + str(format_exc()) + '\n' + str(err)
        queue.put(text)
        send_mail(text, subject='Fail logs works')

def edit_requests(queue):
    try:
        while True:
            queue.put(processing_incoming_json(['clients', 'json'], ['clients', 'users'], ['clients', 'comps'], ['clients', 'dhcp']))
            queue.put(check_base(['clients', 'comps']))
            queue.put(check_base(['clients', 'users']))
            queue.put(check_base(['clients', 'dhcp']))
            time.sleep(360)
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail JSON work\n' + str(format_exc()) + '\n' + str(err)
        queue.put(text)
        send_mail(text, subject='Fail JSON works')

def get_dally_statistics(queue):
    try:
        for i in range(60):
            if datetime.datetime.now().minute == 0:
                while True:
                    for i in range(24):
                        time.sleep(3600)
                        name = "dally-" + str(i)
                        subproc = multiprocessing.Process(name=name, target=processing_statistics_route,
                                                          args=[['clients', 'dhcp'],['clients', 'stat']],
                                                          kwargs={'times' : 'hour', 'queue': queue})
                        subproc.start()
                        if (datetime.datetime.now() - datetime.timedelta(hours=3)).hour == 0:
                            name = 'dally-full'
                            subproc = multiprocessing.Process(name=name, target=processing_statistics_route,
                                                              args=[['clients', 'dhcp'], ['clients', 'stat']],
                                                              kwargs={'times': 'day', 'queue': queue})
                            subproc.start()
            time.sleep(60)
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail daily statistics work\n' + str(format_exc()) + '\n' + str(err)
        queue.put(text)
        send_mail(text, subject='Fail statistics works')


if __name__ == '__main__':
    queue = multiprocessing.Queue()
    proc1 = multiprocessing.Process(name='app', target=application, args=(queue,))
    proc2 = multiprocessing.Process(name='daemon', target=daemon, args=(queue,))
    proc3 = multiprocessing.Process(name='editor', target=edit_requests, args=(queue,))
    proc4 = multiprocessing.Process(name='logs', target=processing_logs, args=(queue,))
    proc5 = multiprocessing.Process(name='dally', target=get_dally_statistics, args=(queue,))
    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()
    proc5.start()
    get_stdout(queue)
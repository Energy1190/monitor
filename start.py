import multiprocessing
import time
import datetime
from webapp import app
from watch import main
from requests_s import delete_old_reqests, check_base, processing_incoming_route, processing_incoming_json

def application():
    app.run(port=5000, host='0.0.0.0')

def daemon():
    main()

def processing_logs():
    while True:
        if not processing_incoming_route(['route', 'incoming'], ['route', 'base']):
            time.sleep(5)

def edit_requests():
    x = 0
    y = 0
    while True:
        processing_incoming_json(['clients', 'json'], ['clients', 'users'], ['clients', 'comps'])
        check_base(['clients', 'comps'])
        check_base(['clients', 'users'])
        time.sleep(360)
        if datetime.datetime.now().day == 20 and x == 0:
            delete_old_reqests(['clients', 'json'])
            x = 1
        elif datetime.datetime.now().day == 21:
            x = 0
        if datetime.datetime.now().hour == 1 and y == 0:
            delete_old_reqests(['route', 'incoming'], status=None)
            delete_old_reqests(['route', 'info'], status=None)
            delete_old_reqests(['route', 'notice'], status=None)
            delete_old_reqests(['route', 'warn'], status=None)
            delete_old_reqests(['route', 'err'], status=None)
            delete_old_reqests(['route', 'over'], status=None)
            y = 1
        elif datetime.datetime.now().hour == 2:
            y = 0

if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc2 = multiprocessing.Process(name='daemon', target=daemon)
    proc3 = multiprocessing.Process(name='editor', target=edit_requests)
    proc4 = multiprocessing.Process(name='logs', target=processing_logs)
    proc1.start()
    proc2.start()
    proc3.start()
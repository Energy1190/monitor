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
        processing_incoming_route(['route', 'warn'], ['route', 'base'])
        processing_incoming_route(['route', 'notice'], ['route', 'base'])
        if not processing_incoming_route(['route', 'info'], ['route', 'base']):
            time.sleep(5)

def edit_requests():
    while True:
        processing_incoming_json(['clients', 'json'], ['clients', 'users'], ['clients', 'comps'])
        check_base(['clients', 'comps'])
        check_base(['clients', 'users'])
        time.sleep(360)

if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc2 = multiprocessing.Process(name='daemon', target=daemon)
    proc3 = multiprocessing.Process(name='editor', target=edit_requests)
    proc4 = multiprocessing.Process(name='logs', target=processing_logs)
    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()
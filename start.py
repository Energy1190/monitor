import multiprocessing
import time
import datetime
from lisen_ps_script import app
from check_site import main
from convert_request import edit_json, delete_old_reqests, check_base

def application():
    app.run(port=5000, host='0.0.0.0')

def daemon():
    main()

def edit_requests():
    x = 0
    y = 0
    while True:
        edit_json()
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

if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc2 = multiprocessing.Process(name='daemon', target=daemon)
    proc3 = multiprocessing.Process(name='editor', target=edit_requests)
    proc1.start()
    proc2.start()
    proc3.start()
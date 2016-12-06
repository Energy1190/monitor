import multiprocessing
import time
from lisen_ps_script import app
from check_site import main
from  convert_request import edit_json

def application():
    app.run(port=5000, host='0.0.0.0')

def daemon():
    main()

def edit_requests():
    while True:
        edit_json()
        time.sleep(360)

if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc2 = multiprocessing.Process(name='daemon', target=daemon)
    proc3 = multiprocessing.Process(name='editor', target=edit_requests)
    proc1.start()
    proc2.start()
    proc3.start()
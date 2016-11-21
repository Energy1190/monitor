import multiprocessing
from lisen_ps_script import app
from check_site import main

def application():
    app.run(port=5000, host='0.0.0.0')

def daemon():
    main()

if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc2 = multiprocessing.Process(name='daemon', target=daemon)
    proc1.start()
    proc2.start()
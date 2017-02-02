import multiprocessing
import time
import datetime
from webapp import app
from watch import main, send_mail
from traceback import format_exc
from processing import processing_statistics_route
from requests_s import delete_old_reqests, check_base, processing_incoming_route, processing_incoming_json, error_log_write, error_c
from reguests_db import target_collection

def application():
    app.debug = True
    app.run(port=5000, host='0.0.0.0')

def daemon():
    main()

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
        send_mail(text)

def edit_requests():
    try:
        while True:
            processing_incoming_json(['clients', 'json'], ['clients', 'users'], ['clients', 'comps'], ['clients', 'dhcp'])
            check_base(['clients', 'comps'])
            check_base(['clients', 'users'])
            time.sleep(360)
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail JSON work\n' + str(format_exc()) + '\n' + str(err)
        send_mail(text)

def get_dally_statistics():
    try:
        while True:
            for i in range(24):
                time.sleep(3600)
                processing_statistics_route(['clients', 'dhcp'],['clients', 'stat'],time='hour')
            processing_statistics_route(['clients', 'dhcp'],['clients', 'stat'],time='day')
    except Exception as err:
        error_log_write(format_exc(), err)
        text = 'Fail daily statistics work\n' + str(format_exc()) + '\n' + str(err)
        send_mail(text)


if __name__ == '__main__':
    proc1 = multiprocessing.Process(name='app', target=application)
    proc2 = multiprocessing.Process(name='daemon', target=daemon)
    proc3 = multiprocessing.Process(name='editor', target=edit_requests)
    proc4 = multiprocessing.Process(name='logs', target=processing_logs)
    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()
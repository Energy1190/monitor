#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import time
import datetime
import multiprocessing
from processing.processing_incoming_route import main as processing_incoming_route
from processing.processing_get_vals import main as processing_get_vals
from requests_s import check_base

def vals():
    while True:
        time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
        target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                      time_now.timetuple()[1],
                                                      time_now.timetuple()[2])
        processing_get_vals(['route', target_collection], ['systems', 'vals'])
        check_base(['clients', 'comps'])
        check_base(['clients', 'users'])
        check_base(['clients', 'dhcp'])
        time.sleep(4000)

if __name__ == '__main__':
    multiprocessing.Process(name='others', target=vals).start()
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
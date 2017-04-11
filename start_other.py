#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import time
import datetime
from classes.vals import Vals
from processing.processing_incoming_route import main as processing_incoming_route

if __name__ == '__main__':
    v = Vals()
    while True:
        time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
        target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                      time_now.timetuple()[1],
                                                      time_now.timetuple()[2])
        processing_incoming_route(['route', 'warn'], ['route', target_collection], v)
        processing_incoming_route(['route', 'notice'], ['route', target_collection], v)
        x = processing_incoming_route(['route', 'info'], ['route', target_collection], v)
        if not x:
            time.sleep(5)
        time.sleep(0.1)
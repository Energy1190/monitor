#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import gc
import sys
import time
import datetime
import logging
import queue
import threading
from traceback import format_exc
from processing.processing_incoming_route import main as processing_incoming_route

if __name__ == '__main__':
    v = None
    q = queue.Queue(maxsize=0)
    try:
        while True:
            time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
            target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                          time_now.timetuple()[1],
                                                          time_now.timetuple()[2])
            for i in processing_incoming_route(['route', 'warn'], ['route', target_collection], v, get_full=True,
                                               output=sys.stdout):
                q.put(i[0])
            for i in processing_incoming_route(['route', 'notice'], ['route', target_collection], v, get_full=True,
                                               output=sys.stdout):
                q.put(i[0])
            for i in processing_incoming_route(['route', 'info'], ['route', target_collection], v, get_full=True,
                                               output=sys.stdout):
                q.put(i[0])

            check_list=[]
            for i in range(0, 5):
                threading.Thread(target=processing_incoming_route, name='route + str(i)', args=(['route', 'warn'], ['route', target_collection], v),
                                 kwargs={'check_list': check_list, 'object': q.get(), 'output': sys.stdout}).start()
                if not q.qsize():
                    break

            start_time = time.localtime()[4]
            while len(check_list) < 5:
                time.sleep(0.1)
                end_time = time.localtime()[4]
                if end_time > start_time + 2:
                    break

            gc.collect()
    except Exception as err:
        logging.error('A critical error occurred while processing logs')
        logging.error(str(format_exc()))
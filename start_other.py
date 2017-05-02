#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import gc
import sys
import time
import datetime
import queue
import threading
from traceback import format_exc
from processing.processing_incoming_route import main as processing_incoming_route

if __name__ == '__main__':
    v = None
    q = queue.Queue(maxsize=0)
    try:
        while True:
            time.sleep(0.1)
            time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
            target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                          time_now.timetuple()[1],
                                                          time_now.timetuple()[2])
            for i in processing_incoming_route(['route', 'warn'], ['route', target_collection], v, get_full=True,
                                               output=sys.stdout)[0]:
                q.put([i, ['route', 'warn']])
            for i in processing_incoming_route(['route', 'notice'], ['route', target_collection], v, get_full=True,
                                               output=sys.stdout)[0]:
                q.put([i, ['route', 'notice']])
            for i in processing_incoming_route(['route', 'info'], ['route', target_collection], v, get_full=True,
                                               output=sys.stdout)[0]:
                q.put([i, ['route', 'info']])

            print('Prepared a queue that contains {0} elements'.format(str(q.qsize())), file=sys.stdout)
            sys.stdout.flush()
            while q.qsize():
                check_list = []
                count = 0
                time.sleep(0.1)
                for i in range(0, 10):
                    threading.Thread(target=processing_incoming_route, name='route + str(i)', args=(q.get()[1], ['route', target_collection], v),
                                     kwargs={'check_list': check_list, 'object': q.get()[0], 'output': sys.stdout}).start()
                    count += 1
                    if not q.qsize():
                        break

                start_time = time.localtime()[4]
                while len(check_list) < count:
                    time.sleep(0.1)
                    end_time = time.localtime()[4]
                    if end_time > start_time + 3:
                        print('Exit by timeout. Counter: {0} list: {1}'.format(str(count), str(check_list)), file=sys.stderr)
                        break

            gc.collect()
            print('The cycle is completed, the beginning of the next iteration.', file=sys.stdout)
            sys.stdout.flush()
    except Exception as err:
        print('A critical error occurred while processing logs', file=sys.stderr)
        print(str(format_exc()), file=sys.stderr)
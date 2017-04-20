#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import gc
import sys
import time
import datetime
import logging
from traceback import format_exc
from processing.processing_incoming_route import main as processing_incoming_route

if __name__ == '__main__':
    v = None
    try:
        while True:
            time_now = (datetime.datetime.now() + datetime.timedelta(hours=3))
            target_collection = 'base-{0}-{1}-{2}'.format(time_now.timetuple()[0],
                                                          time_now.timetuple()[1],
                                                          time_now.timetuple()[2])
            processing_incoming_route(['route', 'warn'], ['route', target_collection], v, output=sys.stdout)
            processing_incoming_route(['route', 'notice'], ['route', target_collection], v, output=sys.stdout)
            if not processing_incoming_route(['route', 'info'], ['route', target_collection], v, output=sys.stdout):
                time.sleep(10)
            time.sleep(0.1)
            gc.collect()
    except Exception as err:
        logging.error('A critical error occurred while processing logs')
        logging.error(str(format_exc()))
#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import time
import logging
from traceback import format_exc
from processing.processing_statistics_route import main as processing_statistics_route
from processing.processing_statistics_route import rebild_statistics as rebild
from processing.processing_statistics_route import check_empty_hours as hours
from processing.processing_statistics_route import check_extra_entries as entries
from processing.processing_maintenance import main as processing_maintenance

if __name__ == '__main__':
    try:
        x = processing_statistics_route(['clients', 'dhcp'], ['clients', 'stat'])
        time.sleep(10)
        hours(['clients', 'dhcp'], ['clients', 'stat'], x[0], x[1])
        entries(['clients', 'stat'], x[0])
        rebild(['clients', 'dhcp'], ['clients', 'stat'], x[0], x[1])
        processing_maintenance()
    except Exception as err:
        logging.error('There was a critical error in the calculation of statistics')
        logging.error(str(format_exc()))

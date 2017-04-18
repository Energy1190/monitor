#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import logging
from traceback import format_exc
from processing.processing_statistics_route import main as processing_statistics_route
from processing.processing_maintenance import main as processing_maintenance

if __name__ == '__main__':
    try:
        processing_statistics_route(['clients', 'dhcp'], ['clients', 'stat'])
        processing_maintenance()
    except Exception as err:
        logging.error('There was a critical error in the calculation of statistics')
        logging.error(str(format_exc()))

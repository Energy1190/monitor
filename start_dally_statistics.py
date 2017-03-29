#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

from processing.processing_statistics_route import processing_statistics_route
from processing.processing_maintenance import main as processing_maintenance

if __name__ == '__main__':
    print('Start dally statistics generate')
    processing_statistics_route(['clients', 'dhcp'], ['clients', 'stat'])
    print('Start maintenance')
    processing_maintenance()

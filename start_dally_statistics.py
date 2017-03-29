#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

from processing.processing_statistics_route import main

if __name__ == '__main__':
    print('Start dally statistics generate')
    main(['clients', 'dhcp'], ['clients', 'stat'])

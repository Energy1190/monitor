#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

from processing.processing_statistics_route import main

print('Start dally statistics generate')
main(['clients', 'dhcp'], ['clients', 'stat'])

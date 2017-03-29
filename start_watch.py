#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

from processing.processing_watch import main
from system.system import watch_pid as check

if __name__ == '__main__':
    print('Start watch for world')
    check()
    main()
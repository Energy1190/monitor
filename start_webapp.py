#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

from web.app import app
from system.system import watch_pid as check

if __name__ == '__main__':
    print('Start web interface')
    check()
    app.debug = True
    app.secret_key = 'not-secret-key'
    app.run(port=5000, host='0.0.0.0')
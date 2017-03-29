#!/usr/bin/env python3
#  -*- coding: utf-8 -*-


from web.app import app
from system.decorate import maintenance
from system.system import watch_pid as check

@maintenance(3600)
def main():
    print('Start web interface')
    check()
    app.debug = True
    app.secret_key = 'not-secret-key'
    app.run(port=5000, host='0.0.0.0')

if __name__ == '__main__':
    main()
#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
    Очищает от повторений список compslist для всех пользователей
'''

import os
import sys
path = '/data/monitor'
if os.path.exists(path):
    if path not in sys.path:
        sys.path.append(path)

from classes.db_mongo import Database

def main():
    t = Database(target=['clients','users']).find()
    if t:
        for i in list(t):
            x = []
            del i['_id']
            if i.get('copmslist'):
                for j in i['copmslist']:
                    if j not in x:
                        x.append(j)
                    else:
                        print('Duplicate {0} in user {1}'.format(str(j), str(i['username'])))
                i['compslist'] = x
            if i.get('compslist'):
                for j in i['compslist']:
                    if j not in x:
                        x.append(j)
                    else:
                        print('Duplicate {0} in user {1}'.format(str(j), str(i['username'])))
                i['compslist'] = x
            Database(target=['clients','users'], fild='username', fild_var=i['username']).update(i)
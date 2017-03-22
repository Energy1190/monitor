#!/usr/bin/env python

import db
import ast
import argparse

def main():
    parser = argparse.ArgumentParser(description='Database API')
    parser.add_argument('command', action='store', help='command', default='find')
    parser.add_argument('-d', '-dict', dest='dict', action='store', help='dict')
    parser.add_argument('-t', '-target', action='store', dest='target', help='target collection',
                        default='clients,users')
    parser.add_argument('-l', '-limit', action='store', dest='limit', help='limit result',
                        default=1)
    parser.add_argument('-f', '-fild', action='store', dest='fild', help='fild',
                        default=None)
    x = parser.parse_args()
    args = []
    kwargs = {}
    if x.dict:
        args.append(ast.literal_eval(x.dict))
    if x.target:
        kwargs['target'] = str(x.target).split(sep=',')
    if x.command == 'find':
        if x.limit:
            kwargs['limit'] = int(x.limit)
        if len(args):
            kwargs['db_dict'] = args[0]
        args = ()
        return print(db.db_find(*args, **kwargs))
    elif x.command == 'find-one':
        kwargs['fild'] = str(x.fild)
        return print(db.db_get(*args, **kwargs))
    elif x.command == 'delete':
        return print(db.db_del(*args, **kwargs))
    elif x.command == 'delete-all':
        return print(db.db_del_all(*args, **kwargs))

if __name__ == '__main__':
    main()
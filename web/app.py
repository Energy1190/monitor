#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import multiprocessing
from flask import Flask, request, render_template, jsonify
from classes.db_mongo import Database
from classes.finder import Router
from processing.processing_incoming_json import main as processing_incoming_json
from reguests_db import get_route_info_database
from system.logmodule import logger
from web.auth import auth

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.__dict__['environ']['REQUEST_METHOD'] == 'POST':
        trg = request.json
        trg['Status'] = 'New'
        Database(dicts=trg, target=['clients', 'json']).set(trg)
        logger.debug('incoming POST: {0}'.format(str(trg)))
        multiprocessing.Process(name='JSON', target= processing_incoming_json,
                                args=[['clients', 'json'], ['clients', 'users'], ['clients', 'comps'], ['clients', 'dhcp']]).start()
    return render_template('index.html', time=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple())

@app.route("/requests/<f_name>/<name>", methods=['GET'])
@auth
def requests_a(f_name, name):
    args_r = {i: request.args.get(i) for i in list(request.args)}
    database_json = Database(dicts=args_r, target=[f_name, name]).find()
    return render_template('requests_route.html', data=database_json, time=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple())

@app.route("/requests/get", methods=['GET'])
@auth
def requests_g():
    args_r = {i: request.args.get(i) for i in list(request.args)}
    if 'limited' not in args_r.keys():
        args_r['limited'] = True
    database_json = get_route_info_database(**args_r)
    return jsonify(result=database_json)

@app.route("/<name>", methods=['GET'])
@auth
def users_p(name):
    debug = False
    names = False
    users = False
    if name in ['comps', 'users', 'dhcp', 'stat']:
        args_r = {i: request.args.get(i) for i in list(request.args)}
        if 'time' in args_r:
            args_r['time'] = list(map(int, args_r['time'].replace('(', '').replace(')', '').split(sep=', ')))
        if 'debug' in args_r:
            debug = True
            del args_r['debug']
            x = Database(dicts=args_r, target=['clients', name], limit=500)
            if x.count(x.find):
                debug = x.count(x.find)
        if name == 'stat':
            database_json = Database(dicts=args_r, target=['clients', name]).get()
            if database_json:
                for i in database_json.get('stat'):
                    if i.get('name'):
                        names = True
                    if i.get('user'):
                        users = True
        else:
            database_json = Database(dicts=args_r, target=['clients', name], limit=500).find()
        return render_template(str(name + '.html'), data=database_json, time=(datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple(),
                               names=names,
                               users=users,
                               debug=debug)
    else:
        return "Not Found 404", 404

@app.route("/finder/<name>", methods=['GET'])
@auth
def form_finder_b(name):
    args_r = {i: request.args.get(i) for i in list(request.args)}
    if 'limited' not in args_r.keys():
        args_r['limited'] = True
    x = Router()
    return render_template('finder.html', time=(datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple(),
                           name=name, form_r=x)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
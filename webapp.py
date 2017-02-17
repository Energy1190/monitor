#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
from shutil import copyfile
from flask import Flask, request, render_template
from db import db_set, db_find, db_get
from requests_s import processing_incoming_json
from reguests_db import get_route_info_database
from configuration import validate_yaml

app = Flask(__name__)

def write_config(x, conf, path, path_t, path_old):
    if x.__dict__['environ']['REQUEST_METHOD'] == 'POST':
        try:
            return validate_yaml(request.form['config'])
        except:
            if os.path.exists(path):
                if os.path.exists(path_old):
                  os.remove(path_old)
                copyfile(path, path_old)
            try:
                if validate_yaml(request.form['config']):
                    file = open(path_t, 'w+')
                    file.writelines(request.form['config'])
                    file.close()
                    copyfile(path_t, path)
                    os.remove(path_t)
                else:
                    return validate_yaml(request.form['config'])
            except:
                if os.path.exists(path):
                    if os.path.exists(path_old):
                      os.remove(path)
                    copyfile(path_old, path)
                    os.remove(path_old)
    return True

def open_config(x, conf, path, path_t):
    try:
        x['validate']
        return x['config']
    except:
        if os.path.exists(path):
            copyfile(path, path_t)
            file = open(path_t, 'r')
            conf = file.read()
            file.close()
            os.remove(path_t)
        return conf

@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.__dict__['environ']['REQUEST_METHOD'] == 'POST':
        trg = request.json
        trg['Status'] = 'New'
        db_set(trg, target=['clients', 'json'])
        try:
            processing_incoming_json(['clients', 'json'], ['clients', 'users'], ['clients', 'comps'], ['clients', 'dhcp'])
        except:
            pass
    return render_template('index.html', time=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple())

@app.route("/config", methods=['POST', 'GET'])
def config():
    path = '/data/config/conf.yaml'
    path_t = '/data/config/conf.tmp'
    path_old = '/data/config/conf.old'
    conf = ''
    write_config(request, conf, path, path_t, path_old)
    conf = open_config(request.form, conf, path, path_t)
    try:
        if validate_yaml(request.form['config']):
            valid = 1
        else:
            valid = 2
    except:
        valid = 0
        if not write_config(conf, path, path_t, path_old):
            valid = 2
    return render_template('config.html', conf=conf, valid=valid, time=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple())

@app.route("/requests/<f_name>/<name>", methods=['GET'])
def requests_a(f_name, name):
    args_r = {i: request.args.get(i) for i in list(request.args)}
    database_json = db_find(args_r, target=[f_name, name])
    return render_template('requests_route.html', data=database_json, time=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple())

@app.route("/requests/get", methods=['GET'])
def requests_g():
    args_r = {i: request.args.get(i) for i in list(request.args)}
    database_json = get_route_info_database(**args_r)
    return render_template('requests_route.html', data=database_json, time=(datetime.datetime.now() + datetime.timedelta(hours=3)).timetuple())

@app.route("/<name>", methods=['GET'])
def users_p(name):
    if name in ['comps', 'users', 'dhcp', 'stat']:
        args_r = {i: request.args.get(i) for i in list(request.args)}
        if 'time' in args_r:
            args_r['time'] = list(map(int, args_r['time'].replace('(', '').replace(')', '').split(sep=', ')))
        if name == 'stat':
            database_json = db_get(args_r, target=['clients', name], fild=None)
        else:
            database_json = db_find(args_r, target=['clients', name], limit=500)
        return render_template(str(name + '.html'), data=database_json, time=(datetime.datetime.now() + datetime.timedelta(hours=2)).timetuple())
    else:
        return "Not Found 404", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




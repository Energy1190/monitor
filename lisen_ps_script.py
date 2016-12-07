#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from shutil import copyfile
from flask import Flask, request, render_template
from db import db_set, db_find
from jsonschema import validate
from convert_request import edit_json
import yaml
import json
import os
import sys

app = Flask(__name__)
def open_config(conf, path, path_t):
    try:
        request.form['validate']
        return request.form['config']
    except:
        if os.path.exists(path):
            copyfile(path, path_t)
            file = open(path_t, 'r')
            conf = file.read()
            file.close()
            os.remove(path_t)
        return conf

def validate_yaml(loads):
    schema = """
    required:
       - users
       - coreos
       - hostname
       - write_files
    """
    try:
        validate(yaml.load(loads), yaml.load(schema))
        yaml.safe_load(loads)
        return True
    except:
        return False

def write_config(conf, path, path_t, path_old):
    if request.__dict__['environ']['REQUEST_METHOD'] == 'POST':
        try:
            request.form['validate']
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

@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.__dict__['environ']['REQUEST_METHOD'] == 'POST':
        trg = request.json
        trg['Status'] = 'New'
        db_set(trg, target=['clients', 'json'])
        try:
            edit_json()
        except:
            pass
    return render_template('index.html')

@app.route("/config", methods=['POST', 'GET'])
def config():
    path = '/data/config/conf.yaml'
    path_t = '/data/config/conf.tmp'
    path_old = '/data/config/conf.old'
    conf = ''
    write_config(conf, path, path_t, path_old)
    conf = open_config(conf, path, path_t)
    try:
        request.form['validate']
        print(validate_yaml(request.form['config']))
        if validate_yaml(request.form['config']):
            valid = 1
        else:
            valid = 2
    except:
        valid = 0
        if not write_config(conf, path, path_t, path_old):
            valid = 2
    return render_template('config.html', conf=conf, valid=valid)

@app.route("/requests", methods=['GET'])
def requests_p():
    database_json = db_find(target=['clients', 'json'])
    return render_template('requests.html', data=database_json)

@app.route("/users", methods=['GET'])
def users_p():
    database_json = db_find(target=['clients', 'users'])
    return render_template('users.html', data=database_json)

@app.route("/comps", methods=['GET'])
def comps_p():
    database_json = db_find(target=['clients', 'comps'])
    return render_template('comps.html', data=database_json)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


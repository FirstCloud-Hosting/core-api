#!flask/bin/python
# -*- coding: utf-8 -*-

# standard modules
import sys
import json
from playhouse.shortcuts import model_to_dict
from peewee import DoesNotExist
from flask_restful import Api, Resource, reqparse
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask import Flask, make_response, jsonify
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired)

# Libs
import utils.configuration
import utils.security
import utils.modules
import utils.emailer
import utils.cache_memcache
import database

# load configuration
config = utils.configuration.load()

if (config['DEFAULT']['MEMCACHED']).lower() == "true":
    cacheEnable = True
    cache = utils.cache_memcache.Cache(
        True,
        config['MEMCACHED']['HOST'],
        config['MEMCACHED']['PORT'])
else:
    cacheEnable = False
    cache = utils.cacheMemcache.Cache(False)

# connect to the database
if database.initialization(
    config['DEFAULT']['DATABASE_MODULE'],
    config['MYSQL']['USERNAME'],
    config['MYSQL']['PASSWORD'],
    config['MYSQL']['DATABASE'],
    config['MYSQL']['HOST'],
    int(
        config['MYSQL']['PORT'])):
    database.make_tables()
else:
    sys.exit(-1)

emailer = utils.emailer.emailer(
    config['SMTP']['SERVER'],
    config['SMTP']['PORT'],
    config['SMTP']['USERNAME'],
    config['SMTP']['PASSWORD'],
    config['SMTP']['ENABLE_TLS'],
    config['DEFAULT']['APP_URL'])

app = Flask(__name__)

app.config['SECRET_KEY'] = config['DEFAULT']['SECRET_KEY']

app.json_encoder = database.JSONEncoder

api = Api(app)

if config['DEFAULT']['ENVIRONMENT']:
    environment = config['DEFAULT']['ENVIRONMENT']
else:
    environment = "production"

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["500 per hour"]
)


@app.route('/1.0/internal/')
def internal():
    return make_response(
        jsonify({'status': 100, 'message': 'API call not found'}), 200)


@app.route('/')
def index():
    return "Welcome to API! Please read documentation at <a href=\"https://docs.linufy.app\">https://docs.linufy.app</a>"


@app.route('/1.0/')
def version():
    return "API Version : 1.4"


@app.errorhandler(404)
def not_found(error):
    return make_response(
        jsonify({'status': 100, 'message': 'API call not found', 'error': error}), 404)

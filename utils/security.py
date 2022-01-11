#!flask/bin/python
# -*- coding: utf-8 -*-

import os
import json
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired)
from flask import jsonify, make_response, request
from playhouse.shortcuts import model_to_dict
import email_validator

import utils.configuration
import database

def validate_password(organization_id, password):

    if organization_id is not None:

        # get organization informations
        query = database.Organizations.get(
            database.Organizations.id == organization_id)

    if organization_id is not None and query.passwordHardening == 1:

        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
        lowercase = 'abcdefghijklmnopqrstuvxyz'
        special_chars = '[@_!#$%^&*()<>?/\\|}{~:]'
        numbers = '0123456789'

        if len(password) < 12:
            return False

        if not len([x for x in password if x in uppercase]) >= 1:
            return False

        if not len([x for x in password if x in lowercase]) >= 1:
            return False

        if not len([x for x in password if x in special_chars]) >= 1:
            return False

        if not len([x for x in password if x in numbers]) >= 1:
            return False

        return True

    if len(password) < 8:
        return False

    return True


def validate_email(email):

    # check if syntax is valid
    try:
        email_validator.validate_email(email)
    except BaseException:
        return False

    # check if domain is in blacklist
    with open('%s/../files/domains.json' % os.path.split(__file__)[0], 'r') as domains_file:
        banned_emails = json.load(domains_file)
        domain = email.split('@')[1].lower()
        if domain in banned_emails:
            return False

    try:
        # check if user already exists with this email
        query = database.Users.get(database.Users.email == email)

        if query:
            return query.id
    except BaseException:
        pass
    return True


def get_user_id(token):

    configuration = utils.configuration.load()

    serializer = Serializer(configuration['DEFAULT']['SECRET_KEY'])

    try:
        data = serializer.loads(token)
        return data['id']
    except BaseException:
        return False


def authentication_required(func):

    def wrapper(*args, **kwargs):

        class_handler = args[0]

        parameters = class_handler.reqparse.parse_args()

        try:

            # check if token parameter is available
            if 'token' not in parameters or parameters['token'] is None:
                response = make_response(
                    jsonify(
                        {'message': {'token': "Token is required for authentication"}}
                    ),
                    400,
                )
                return response

        # valid token, but expired
        except SignatureExpired:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Expired token'}
                ),
                403,
            )
            return response

        # invalid token
        except BadSignature:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Invalid token'}
                ),
                403,
            )
            return response

        return func(*args, **kwargs)

    return wrapper


def allowed_permissions(module):

    def func_wrapper(func):

        def wrapper(*args, **kwargs):

            class_handler = args[0]

            parameters = class_handler.reqparse.parse_args()

            user_id = get_user_id(parameters['token'])

            if isinstance(module, str):

                query = (
                    database.Permissions.select() .join(
                        database.Modules) .switch(
                        database.Permissions) .join(
                        database.Groups) .join(
                        database.Users) .where(
                        database.Users.id == user_id,
                        database.Modules.page == module))

                if len(query) != 0:

                    # get HTTP method
                    method = func.__name__

                    # check if HTTP method is valid
                    if method not in ["get", "post", "put", "delete"]:
                        response = make_response(
                            jsonify(
                                {'status': 100, 'message': 'Method not allowed'}
                            ),
                            405,
                        )
                        return response

                    if method == "get" and query[0].view == 1:
                        return func(*args, **kwargs)
                    if method == "post" and query[0].creation == 1:
                        return func(*args, **kwargs)
                    if method == "put" and query[0].edition == 1:
                        return func(*args, **kwargs)
                    if method == "delete" and query[0].deletion == 1:
                        return func(*args, **kwargs)

                    response = make_response(
                        jsonify(
                            {'status': 100, 'message': 'Permissions denied'}
                        ),
                        403,
                    )
                    return response

                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Permissions denied'}
                    ),
                    403,
                )
                return response

            else:

                for m in module:

                    query = (
                        database.Permissions.select() .join(
                            database.Modules) .switch(
                            database.Permissions) .join(
                            database.Groups) .join(
                            database.Users) .where(
                            database.Users.id == user_id,
                            database.Modules.page == m))

                    if len(query) != 0:

                        # get HTTP method
                        method = func.__name__

                        # check if HTTP method is valid
                        if method not in ["get", "post", "put", "delete"]:
                            response = make_response(
                                jsonify(
                                    {'status': 100, 'message': 'Method not allowed'}
                                ),
                                405,
                            )
                            return response

                        if method == "get" and query[0].view == 1:
                            return func(*args, **kwargs)
                        if method == "post" and query[0].creation == 1:
                            return func(*args, **kwargs)
                        if method == "put" and query[0].edition == 1:
                            return func(*args, **kwargs)
                        if method == "delete" and query[0].deletion == 1:
                            return func(*args, **kwargs)

                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Permissions denied'}
                    ),
                    403,
                )
                return response

        return wrapper

    return func_wrapper


def get_ip():
    # get IP address for user
    if request.headers.getlist("X-Forwarded-For"):
        remote_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        remote_ip = request.remote_addr
    return remote_ip

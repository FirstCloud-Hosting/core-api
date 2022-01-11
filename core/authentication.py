#!flask/bin/python
# -*- coding: utf-8 -*-
"""Authentication module allows to authenticate users and applications to API
"""

from common import *

# Authentication for user


class AuthenticateUserAPI(Resource):

    """Authenticate user to API

    Attributes:
        token (str): Token if user is already connected
        email (str): Email of user
        password (str): Password of user
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token', type=str, help="Token for Authentication")
        self.reqparse.add_argument(
            'email', type=str, help='Email for Authentication')
        self.reqparse.add_argument(
            'password',
            type=str,
            help='Password for Authentication')
        self.reqparse.add_argument('X-Forwarded-For', location='headers')
        super().__init__()

    @utils.security.authentication_required
    def get(self):
        """Get if user is already authenticated and if token is valid

        Returns:
            id: ID of user (UUID format)
        """
        args = self.reqparse.parse_args()

        return jsonify({'status': 200, 'data': {
                       'user_id': utils.security.get_user_id(args['token'])}})

    def post(self):
        """Authenticate user
        """
        args = self.reqparse.parse_args()

        if args['X-Forwarded-For'] is not None:
            remote_ip = args['X-Forwarded-For']
        else:
            remote_ip = utils.security.get_ip()

        # get hash of password
        hash = utils.cryptography.hash_password(args['password'])

        try:
            # authentication by email
            if 'email' not in args or args['email'] is None:
                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Invalid email address'}
                    ),
                    403,
                )
                return response

            user = database.Users.get(
                database.Users.email == args['email'],
                database.Users.password == hash)

            if user:
                # create session
                s = Serializer(
                    app.config['SECRET_KEY'], expires_in=int(
                        config['DEFAULT']['SESSION_LIFETIME']))
                token = s.dumps({'id': str(user.id)}).decode()

                # log activity
                database.ActivityLogs.create(
                    activity="Autentication",
                    result="%s - %s : Authentication success" %
                    args['email'], remote_ip)

                return jsonify(
                    {
                        'status': 200,
                        'data': {
                            'token': token,
                            'user_id': user.id,
                            'group_id': user.group_id,
                            'expiration': int(
                                config['DEFAULT']['SESSION_LIFETIME'])}})

            else:
                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Authentication failure'}
                    ),
                    403,
                )
                return response

        except DoesNotExist:

            # log activity
            database.ActivityLogs.create(
                activity="Autentication",
                result="%s : Authentication failure" %
                args['email'])

            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Authentication failure'}
                ),
                403,
            )
            return response


api.add_resource(AuthenticateUserAPI, '/1.0/authentication')


# Authentication for application
class AuthenticateAppAPI(Resource):

    """Authenticate application to API

    Attributes:
        token (str): Token if application is already connected
        organizationKey (str): Organization key (same key for all applications key created by an organization)
        secretKey (str): Secret key is
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token', type=str, help="Token for Authentication")
        self.reqparse.add_argument(
            'organizationKey',
            type=str,
            help='Organization Key for Authentication')
        self.reqparse.add_argument(
            'secretKey',
            type=str,
            help='Secret Key for Authentication')
        self.reqparse.add_argument('X-Forwarded-For', location='headers')
        super().__init__()

    @utils.security.authentication_required
    def get(self):
        """Summary

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        return jsonify({'status': 200, 'data': {
                       'user_id': utils.security.get_user_id(args['token'])}})

    def post(self):
        """Summary

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        if args['X-Forwarded-For'] is not None:
            remote_ip = args['X-Forwarded-For']
        else:
            remote_ip = get_ip()

        try:
            # get user
            if 'organizationKey' in args and args['organizationKey'] is not None and 'secretKey' in args and args['secretKey'] is not None:
                user = (
                    database.AppKeys.select() .join(
                        database.Users) .where(
                        database.Users.organization_id == args['organizationKey'],
                        database.AppKeys.secretKey == args['secretKey']))

            if user:
                # create session
                s = Serializer(
                    app.config['SECRET_KEY'], expires_in=int(
                        config['DEFAULT']['SESSION_LIFETIME']))
                token = s.dumps({'id': str(user[0].user_id)}).decode()

                # log activity
                database.ActivityLogs.create(
                    activity="Autentication", result="%s - %s - %s : Application authentication success" %
                    (args['organizationKey'], args['secretKey'], remote_ip))

                return jsonify(
                    {
                        'status': 200,
                        'data': {
                            'token': token,
                            'user_id': user[0].user_id,
                            'group_id': user[0].user.group_id,
                            'expiration': int(
                                config['DEFAULT']['SESSION_LIFETIME'])}})

            else:
                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Application authentication failure'}
                    ),
                    403,
                )
                return response

        except DoesNotExist:

            # log activity
            database.ActivityLogs.create(
                activity="Autentication", result="%s - %s : Application authentication failure" %
                (args['organizationKey'], args['secretKey']))

            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Application authentication failure'}
                ),
                403,
            )
            return response


api.add_resource(AuthenticateAppAPI, '/1.0/authenticationApp')

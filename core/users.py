#!flask/bin/python
# -*- coding: utf-8 -*-
"""Users module
"""

import hashlib
from uuid import uuid4
from flask import jsonify, make_response
from common import *


class UsersListAPI(Resource):

    """List all users
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token', type=str, help='Token is required for authentication')
        self.reqparse.add_argument(
            'email', type=str, help='Email address for new user')
        self.reqparse.add_argument(
            'password', type=str, help='Password for new user')
        self.reqparse.add_argument(
            'group_id', type=str, help='Group for new user')
        self.reqparse.add_argument(
            'organization_id',
            type=str,
            help="ID of the associated organization to user")
        super().__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/users')
    def get(self):
        """Get all users

        Returns:
            dict: list of users
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        # Get all groups for organization
        query = (
            database.Users.select() .where(
                database.Users.organization_id == user.organization_id))

        query = [model_to_dict(item) for item in query]
        return jsonify({'status': 200, 'data': query})

    def post(self):
        """Create an user
        """
        args = self.reqparse.parse_args()

        if not args['email'] or not args['password']:
            return {
                'status': 100,
                'message': 'password or email is not defined'}

        if args['token']:

            # get current user ID
            user_id = utils.security.get_user_id(args['token'])

            # get SQL user instance
            user = database.Users.get(database.Users.id == user_id)

            if utils.security.validate_password(
                    user.organization_id, args['password']) == False:
                return {'status': 100, 'message': 'Invalid password'}

        else:

            if utils.security.validate_password(
                    None, args['password']) == False:
                return {'status': 100, 'message': 'Invalid password'}

            user_id = None

        if utils.security.validate_email(args['email']) != True:
            return {'status': 100, 'message': 'Invalid email address'}

        if user_id is not None:

            # get permission
            query = (
                database.Permissions.select() .join(
                    database.Modules) .switch(
                    database.Permissions) .join(
                    database.Groups) .join(
                    database.Users) .where(
                        database.Users.id == user_id,
                    database.Modules.page == 'core/users'))

            if len(query) != 0:

                if 'group_id' not in args:
                    return {'status': 100,
                            'message': 'group_id is not defined'}

                group_id = args['group_id']
                organization_id = user.organization_id

            else:

                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Permissions denied'}
                    ),
                    403,
                )
                return response

        else:

            # get organization_id by parameters or create new organization if
            # parameter is not defined
            if not args['organization_id']:
                if environment == "demo":
                    organization_id = database.Organizations.create(
                        validity=str(config['DEFAULT']['DEMO_VALIDITY']))
                else:
                    organization_id = database.Organizations.create()
            else:
                organization_id = args['organization_id']

            # create group for new user and organization
            group_id = database.Groups.create(
                organization_id=organization_id,
                name='Administrators',
                note='All Administrators')

            # create all permissions for the new group
            query = database.Modules.select().where(database.Modules.forAdmin == 0)
            query = [model_to_dict(item) for item in query]
            for module in query:
                database.Permissions.create(module_id=module['id'],
                                            group_id=group_id,
                                            creation=1,
                                            edition=1,
                                            deletion=1)

        # generate validation key
        key = str(uuid4())

        # get hash of password
        hash_password = utils.cryptography.hash_password(args['password'])

        language_id = database.Languages.get(
            database.Languages.name == 'English')

        user = database.Users.create(organization_id=organization_id,
                                     group_id=group_id,
                                     email=args['email'],
                                     password=hash_password,
                                     confirmKey=key,
                                     language_id=language_id)

        if 'group_id' not in args:
            emailer.send_confirm_signup(
                'welcome@linufy.app',
                args['email'],
                'LinuFy - Welcome !',
                key)
        else:
            forgot_password_key = str(uuid4())

            query = database.Users.update(
                forgotPasswordKey=forgot_password_key).where(
                database.Users.id == user.id)
            query.execute()

            emailer.send_lost_password(
                'lost_password@linufy.app',
                args['email'],
                'FirstCloud-Hosting - Password Reset',
                forgot_password_key)

        return {'status': 200, 'message': 'User successfully created'}


class UserAPI(Resource):

    """Get an user
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Tocken is required for authentication')
        self.reqparse.add_argument(
            'currentPassword',
            type=str,
            help="Current password for edit user")
        self.reqparse.add_argument(
            'email', type=str, help='Email address for edit user')
        self.reqparse.add_argument(
            'status', type=str, help='Status for edit user')
        self.reqparse.add_argument(
            'groupId', type=str, help='Group for edit user')
        self.reqparse.add_argument(
            'languageId',
            type=str,
            help="languageId for edit user")
        super().__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/users')
    def get(self, user_id):
        """Get an user

        Args:
            user_id (str): User ID (UUID format)

        Returns:
            dict: User informations
        """
        args = self.reqparse.parse_args()

        # get current user ID
        current_user_id = utils.security.get_user_id(args['token'])

        # get current SQL user instance
        user = database.Users.get(database.Users.id == current_user_id)

        # get user_id SQL user instance
        query = database.Users.get(
            database.Users.id == user_id,
            database.Users.organization_id == user.organization_id)
        return jsonify({'status': 200, 'data': model_to_dict(query)})

    @utils.security.authentication_required
    def put(self, user_id):
        """Edit an user

        Args:
            user_id (str): User ID (UUID format)
        """
        args = self.reqparse.parse_args()

        # get current user ID
        current_user_id = utils.security.get_user_id(args['token'])

        check_email_address = utils.security.validate_email(args['email'])

        if check_email_address != current_user_id and check_email_address == False:
            return {'status': 100, 'message': 'Invalid email address'}

        # current user
        if current_user_id == user_id:

            # get current SQL user instance
            user = database.Users.get(database.Users.id == current_user_id)

            if 'currentPassword' not in args or utils.cryptography.hash_password(
                    args['currentPassword']) != user.password:
                return {
                    'status': 100,
                    'message': 'Current password is invalid'}

            query = database.Users.update(
                email=args['email'],
                language_id=args['languageId']).where(
                database.Users.id == current_user_id)
            query.execute()
            return {'status': 200, 'message': 'User successfully updated'}

        # not current user
        else:

            # get permission
            query = (
                database.Permissions.select() .join(
                    database.Modules) .switch(
                    database.Permissions) .join(
                    database.Groups) .join(
                    database.Users) .where(
                        database.Users.id == current_user_id,
                    database.Modules.page == 'core/users'))

            if len(query) == 0:
                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Permissions denied'}
                    ),
                    403,
                )
                return response

            if 'groupId' not in args:
                return {'status': 100, 'message': 'groupId not set'}

            if current_user_id == user_id:
                return {
                    'status': 100,
                    'message': 'Unable to change group of current user'}

            query = database.Users.update(
                email=args['email'],
                group_id=args['groupId']).where(
                database.Users.id == user_id)
            query.execute()
            return {'status': 200, 'message': 'User successfully updated'}

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/users')
    def delete(self, user_id):
        """Delete an user

        Args:
            user_id (str): User ID (UUID format)
        """
        args = self.reqparse.parse_args()

        # get current user ID
        current_user_id = utils.security.get_user_id(args['token'])

        if current_user_id == user_id:
            return {'status': 100, 'message': 'Cannot delete current user'}

        # get current SQL user instance
        user = database.Users.get(database.Users.id == current_user_id)

        # delete permissions for group
        query = database.Users.delete().where(
            database.Users.id == user_id,
            database.Users.organization_id == user.organization_id)
        query.execute()
        return {'status': 200, 'message': 'User successfully deleted'}


class UserMfaAPI(Resource):

    """Summary

    Attributes:
        reqparse (TYPE): Description
    """

    def __init__(self):
        """Summary
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument(
            'mfa',
            type=str,
            required=True,
            help='Status of Multi Factor Authentication')
        self.reqparse.add_argument(
            'mfaKey',
            type=str,
            required=True,
            help='Secret Key of Multi Factor Authentication')
        super().__init__()

    @utils.security.authentication_required
    def put(self):
        """Summary

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        if args['mfa'] in ['on', 'off']:

            # set MFA configuration for current user
            query = database.Users.update(
                mfa=args['mfa'], mfaKey=args['mfaKey']).where(
                database.Users.id == user_id)
            query.execute()
            return {
                'status': 200,
                'message': 'Multi factor authentication has been successfully configured'}

        else:
            return {
                'status': 100,
                'message': 'Invalid status of multi factor authentication'}
        return True


class UserPasswordAPI(Resource):

    """Summary

    Attributes:
        reqparse (TYPE): Description
    """

    def __init__(self):
        """Summary
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token', type=str, help='Username for Authentication')
        self.reqparse.add_argument(
            'currentPassword',
            type=str,
            help="Current password for edit user")
        self.reqparse.add_argument(
            'forgotPasswordKey',
            type=str,
            help='Email address for edit user')
        self.reqparse.add_argument(
            'password', type=str, help='Password for edit user')
        super().__init__()

    def put(self):
        """Summary

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        if 'password' not in args:
            return {'status': 100, 'message': 'Invalid new password'}

        if 'token' in args and args['token'] is not None:

            # get current user ID
            current_user_id = utils.security.get_user_id(args['token'])

            # get current SQL user instance
            user = database.Users.get(database.Users.id == current_user_id)

            if 'currentPassword' not in args or utils.cryptography.hash_password(
                    args['currentPassword']) != user.password:
                return {
                    'status': 100,
                    'message': 'Current password is invalid'}

        elif 'forgotPasswordKey' in args:

            try:
                # get current SQL user instance
                user = database.Users.get(
                    database.Users.forgotPasswordKey == args['forgotPasswordKey'])
            except BaseException:
                response = make_response(
                    jsonify(
                        {'status': 100, 'message': 'Permissions denied'}
                    ),
                    403,
                )
                return response

        else:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Permissions denied'}
                ),
                403,
            )
            return response

        hash_password = utils.cryptography.hash_password(args['password'])

        query = database.Users.update(
            password=hash_password,
            status=1).where(
            database.Users.id == user.id)
        query.execute()
        return {'status': 200, 'message': 'User password successfully updated'}


class UserLostPasswordAPI(Resource):

    """Summary

    Attributes:
        decorators (TYPE): Description
        reqparse (TYPE): Description
    """

    decorators = [
        limiter.limit("5/hour"),
    ]

    def __init__(self):
        """Summary
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'email',
            type=str,
            required=True,
            help='Email for lost account password')
        super().__init__()

    def post(self):
        """Summary

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        try:
            # get current SQL user instance
            user = database.Users.get(database.Users.email == args['email'])

        except BaseException:
            return {'status': 100, 'message': 'Invalid email address'}

        if user:

            if user.status != 1:
                return {'status': 100, 'message': 'Account not active'}

            forgot_password_key = str(uuid4())

            query = database.Users.update(
                forgotPasswordKey=forgot_password_key).where(
                database.Users.id == user.id)
            query.execute()

            emailer.sendLostPassword(
                'lost_password@linufy.app',
                args['email'],
                'FirstCloud-Hosting - Password Reset',
                forgot_password_key)

            return {'status': 200, 'data': 'Successfully sent'}


class UserConfirmSignUpAPI(Resource):

    """Summary

    Attributes:
        decorators (TYPE): Description
        reqparse (TYPE): Description
    """

    decorators = [
        limiter.limit("5/hour"),
    ]

    def __init__(self):
        """Summary
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'email',
            type=str,
            required=True,
            help='Email for your account')
        self.reqparse.add_argument(
            'confirmKey',
            type=str,
            required=True,
            help='Key for confirm your account')
        super().__init__()

    def post(self):
        """Summary

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        try:
            # get current SQL user instance
            user = database.Users.get(database.Users.email == args['email'])

        except BaseException:
            return {'status': 100, 'message': 'Invalid email address'}

        if str(user.confirmKey) == args['confirmKey']:
            query = database.Users.update(
                status=1).where(
                database.Users.id == user.id)
            query.execute()
            return {'status': 200, 'data': 'User successfully actived'}

        else:
            return {
                'status': 100,
                'message': 'User yet active or confirm key is invalid'}


class UserStatusAPI(Resource):

    """Summary

    Attributes:
        reqparse (TYPE): Description
    """

    def __init__(self):
        """Summary
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Username for Authentication')
        self.reqparse.add_argument(
            'status',
            type=int,
            required=True,
            help='Status for edit user')
        super().__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/users')
    def put(self, user_id):
        """Summary

        Args:
            user_id (TYPE): Description

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        # get current user ID
        current_user_id = utils.security.get_user_id(args['token'])

        if user_id == current_user_id:
            return {'status': 100, 'message': 'Unable to edit current user'}

        if not args['status'] in [0, 1]:
            return {'status': 100, 'message': 'Invalid status'}

        # get current SQL user instance
        user = database.Users.get(database.Users.id == current_user_id)

        try:
            query = database.Users.update(
                status=args['status']).where(
                database.Users.id == user_id)
            query.execute()
            return {'status': 200, 'data': 'User status changed'}
        except BaseException:
            return {'status': 100, 'message': 'Invalid user'}


class UsersCountAPI(Resource):

    """Summary

    Attributes:
        reqparse (TYPE): Description
    """

    def __init__(self):
        """Summary
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Username for Authentication')
        super().__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/users')
    def get(self):
        """Summary

        Returns:
            TYPE: Description
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        query = database.Users.select().where(
            database.Users.organization_id == user.organization_id).count()

        return {'status': 200, 'data': query}


api.add_resource(UsersListAPI, '/1.0/users')
api.add_resource(UserAPI, '/1.0/users/<string:user_id>')
api.add_resource(UserPasswordAPI, '/1.0/users/password')
api.add_resource(UserMfaAPI, '/1.0/users/mfa')
api.add_resource(UserStatusAPI, '/1.0/users/<string:user_id>/status')
api.add_resource(UserConfirmSignUpAPI, '/1.0/users/confirm')
api.add_resource(UserLostPasswordAPI, '/1.0/users/lostPassword')
api.add_resource(UsersCountAPI, '/1.0/users/count')

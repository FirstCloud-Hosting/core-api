#!flask/bin/python
# -*- coding: utf-8 -*-
"""app keys are API keys used for authenticate application to API
"""

from common import *


class AppKeysListsAPI(Resource):

    """List all app keys

    Attributes:
        token (str): Token used for validate user authentication
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        super().__init__()

    @utils.security.authentication_required
    def get(self):
        """List app keys

        Returns:
            dict: list of app keys
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # Get all applications keys for user
        query = (database.AppKeys.select()
                 .where(database.AppKeys.user_id == user_id))

        query = [model_to_dict(item) for item in query]
        data = json.dumps(query, cls=database.JSONEncoder)
        return jsonify({'status': 200, 'data': query})

    @utils.security.authentication_required
    def post(self):
        """Create app key

        Returns:
            id: ID of new app key (UUID format)
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        app_key = database.AppKeys.create(user_id=user_id)

        return jsonify({'status': 200,
                        'message': 'Application Key successfully added',
                        'id': app_key.id})


class AppKeysAPI(Resource):

    """Selected app key

    Attributes:
        token (str): Token used for validate user authentication
        description (str): Description of your app key
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument(
            'description',
            type=str,
            help='Description of your application')
        super().__init__()

    @utils.security.authentication_required
    def get(self, appKey_id):
        """Get selected app key

        Args:
            appKey_id (str): app key ID (UUID format)

        Returns:
            dict: informations of selected app key
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        query = database.AppKeys.get(
            database.AppKeys.id == appKey_id,
            database.AppKeys.user_id == user_id)
        return jsonify({'status': 200, 'data': model_to_dict(query)})

    @utils.security.authentication_required
    def put(self, appKey_id):
        """Edit selected app key

        Args:
            appKey_id (str): app key ID (UUID format)
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # update group
        query = database.AppKeys.update(
            description=args['description']).where(
            database.AppKeys.id == appKey_id,
            database.AppKeys.user_id == user_id)
        query.execute()
        return {'status': 200, 'message': 'Application Key successfully edited'}

    @utils.security.authentication_required
    def delete(self, appKey_id):
        """Delete selected app key

        Args:
            appKey_id (str): app key ID (UUID format)
        """
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # delete group
        query = database.AppKeys.delete().where(
            database.AppKeys.id == appKey_id,
            database.AppKeys.user_id == user_id)
        query.execute()
        return {
            'status': 200,
            'message': 'Application Key successfully deleted'}


api.add_resource(AppKeysListsAPI, '/1.0/appKeys')
api.add_resource(AppKeysAPI, '/1.0/appKeys/<string:appKey_id>')

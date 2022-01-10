#!flask/bin/python

from common import *

class PermissionsListsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument(
            'permissions',
            type=str,
            help='List of permissions')
        super(PermissionsListsAPI, self).__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/groups')
    def get(self, group_id):
        # get parameters
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        user = database.Users.get(database.Users.id == user_id)

        group = database.Groups.get(database.Groups.id == group_id)

        if group.organization_id == user.organization_id:

            # Get all permissions for an group
            query = database.Permissions.select().where(
                database.Permissions.group_id == group_id)
            query = [model_to_dict(item) for item in query]
            return jsonify({'status': 200, 'data': query})

        else:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'You can not get this group'}
                ),
                403,
            )
            return response

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/groups')
    def put(self, group_id):
        # get parameters
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        data = database.Users.get(database.Users.id == user_id)

        if data.group_id == group_id:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'You can not edit your group'}
                ),
                403,
            )
            return response

        permissions = json.loads(args['permissions'])

        # delete permissions for group
        query = database.Permissions.delete().where(
            database.Permissions.group_id == group_id)
        query.execute()

        array = []

        for permission in permissions:

            if 'creation' in permissions[permission] and 'edition' in permissions[
                    permission] and 'deletion' in permissions[permission]:

                array.append({'module_id': permission,
                              'group_id': group_id,
                              'creation': int(permissions[permission]['creation']),
                              'edition': int(permissions[permission]['edition']),
                              'deletion': int(permissions[permission]['deletion'])})

        database.Permissions.insert_many(array).execute()

        return {
            'status': 200,
            'message': 'Permissions successfully added/edited'}


api.add_resource(
    PermissionsListsAPI,
    '/1.0/groups/<string:group_id>/permissions')

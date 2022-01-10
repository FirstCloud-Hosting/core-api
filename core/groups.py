#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *


class GroupsListsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument('name', type=str, help='Group name')
        self.reqparse.add_argument('note', type=str, help='Note for the group')
        super(GroupsListsAPI, self).__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/groups')
    def get(self):
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        # Get all groups for organization
        query = (
            database.Groups.select() .where(
                database.Groups.organization_id == user.organization_id) .order_by(
                database.Groups.name))

        query = [model_to_dict(item) for item in query]
        data = json.dumps(query, cls=database.JSONEncoder)
        return jsonify({'status': 200, 'data': query})

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/groups')
    def post(self):
        args = self.reqparse.parse_args()

        if not args['name'] or not args['note']:
            return {'status': 100, 'message': 'name or note is not defined'}

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        user = database.Users.get(database.Users.id == user_id)

        group = database.Groups.create(
            organization_id=user.organization_id,
            name=args['name'],
            note=args['note'])

        return jsonify({'status': 200,
                        'message': 'Group successfully added',
                        'id': group.id})


class GroupAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument('name', type=str, help='Group name')
        self.reqparse.add_argument('note', type=str, help='Note for the group')
        super(GroupAPI, self).__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/groups')
    def get(self, group_id):
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        # get permission
        query = (
            database.Permissions.select() .join(
                database.Modules) .switch(
                database.Permissions) .join(
                database.Groups) .join(
                    database.Users) .where(
                        database.Users.id == user_id,
                database.Modules.page == 'core/groups'))

        try:

            if len(query) != 0:

                query = database.Groups.get(
                    database.Groups.id == group_id,
                    database.Groups.organization_id == user.organization_id)
                return jsonify({'status': 200, 'data': model_to_dict(query)})

            else:

                query = database.Groups.get(
                    database.Groups.id == user.group_id,
                    database.Groups.organization_id == user.organization_id)
                return jsonify({'status': 200, 'data': model_to_dict(query)})

        except BaseException:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Group not found'}
                ),
                404,
            )
            return response

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/groups')
    def put(self, group_id):
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        if group_id == user.group_id:
            return {'status': 100, 'message': 'Cannot edit current group'}

        if args['name'] == '' or args['note'] == '':
            return {'status': 100, 'message': 'Cannot edit group'}

        # update group
        query = database.Groups.update(
            name=args['name'],
            note=args['note']).where(
            database.Groups.id == group_id,
            database.Groups.organization_id == user.organization_id)
        query.execute()
        return {'status': 200, 'message': 'Group successfully edited'}

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/groups')
    def delete(self, group_id):
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        if group_id == user.group_id:
            return {'status': 100, 'message': 'Cannot delete current group'}

        # delete permissions for group
        query = database.Permissions.delete().where(
            database.Permissions.group_id == group_id)
        query.execute()

        # delete group
        query = database.Groups.delete().where(
            database.Groups.id == group_id,
            database.Groups.organization_id == user.organization_id)
        query.execute()
        return {'status': 200, 'message': 'Group successfully deleted'}


api.add_resource(GroupsListsAPI, '/1.0/groups')
api.add_resource(GroupAPI, '/1.0/groups/<string:group_id>')

#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *


class ModulesListsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument('name', type=str, help='Module name')
        self.reqparse.add_argument('page', type=str, help='Module Resource')
        self.reqparse.add_argument('type_id', type=str, help='Type ID')
        self.reqparse.add_argument(
            'forAdmin',
            type=bool,
            help='This module is reserved for admin ?')
        super().__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions(['core/modules', 'core/groups'])
    def get(self):
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        # get permission
        query = (database.Permissions.select()
                .join(database.Modules)
                .switch(database.Permissions)
                .join(database.Groups)
                .join(database.Users)
                .where(database.Users.id == user_id, database.Modules.page == 'core/modules'))

        if len(query) != 0:

            query = (database.Permissions.select()
              .join(database.Modules)
              .join(database.Types)
              .where(database.Permissions.group_id == user.group_id))
            query = [model_to_dict(item) for item in query]

            return jsonify({'status': 200, 'data': query})

        # get permission
        query = (database.Permissions.select()
                .join(database.Modules)
                .switch(database.Permissions)
                .join(database.Groups)
                .join(database.Users)
                .where(database.Users.id == user_id, database.Modules.page == 'core/groups'))

        if len(query) != 0:

            query = (database.Permissions.select()
              .join(database.Modules)
              .join(database.Types)
              .where(database.Modules.forAdmin == 0, database.Permissions.group_id == user.group_id))

            query = [model_to_dict(item) for item in query]

            return jsonify({'status': 200, 'data': query})

        return None

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/modules')
    def post(self):
        args = self.reqparse.parse_args()

        try:
            # get if module exist
            module = database.Modules.get(
                database.Modules.page == args['page'])

            return {'status': 100, 'message': 'This module already exist'}

        except DoesNotExist:
            module = database.Modules.create(
                type_id=args['type_id'],
                name=args['name'],
                page=args['page'],
                forAdmin=args['forAdmin'])

            return jsonify({'status': 200,
                'message': 'Module successfully added',
                'id': module.id})


class ModuleAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
    'token',
    type=str,
    required=True,
     help='Token is required for authentication')
        self.reqparse.add_argument('name', type=str, help='Module name')
        self.reqparse.add_argument('page', type=str, help='Module Resource')
        self.reqparse.add_argument('type_id', type=str, help='Type ID')
        self.reqparse.add_argument(
    'forAdmin',
    type=bool,
     help='This module is reserved for admin ?')
        super().__init__()

    @utils.security.authentication_required
    def get(self, module_id):
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get SQL user instance
        user = database.Users.get(database.Users.id == user_id)

        # get permission
        query = (database.Permissions.select()
                .join(database.Modules)
                .switch(database.Permissions)
                .join(database.Groups)
                .join(database.Users)
                .where(database.Users.id == user_id, database.Modules.page == 'core/modules'))

        if len(query) != 0:

            query = database.Modules.get(database.Modules.id == module_id)
            return jsonify({'status' : 200,  'data' : model_to_dict(query)})

        try: 
            # get permission
            query = (database.Permissions.get(database.Permissions.group_id == user.group_id, database.Permissions.module_id == module_id))

            query = database.Modules.get(database.Modules.id == module_id)
            return jsonify({'status' : 200,  'data' : model_to_dict(query)})

        except BaseException:
            response = make_response(
                jsonify(
                    {'status' : 100, 'message' : 'You can not get this module'}
                ),
                403,
            )
            return response

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/modules')
    def put(self, module_id):
        args = self.reqparse.parse_args()

        if args['name'] == '' or args['page'] == '' or args['type_id'] == '' or args['forAdmin'] == '':
            return {'status' : 100, 'message' : 'Cannot edit module'}

        # update module
        query = database.Modules.update(name=args['name'], page=args['page'], type=args['type_id'], forAdmin=args['forAdmin']).where(database.Modules.id == module_id)
        query.execute()
        return {'status' : 200, 'message' : 'Module successfully edited'}

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/modules')
    def delete(self, module_id):
        # delete permissions for module
        query = database.Permissions.delete().where(database.Permissions.module_id == module_id)
        query.execute()

        # delete module
        query = database.Modules.delete().where(database.Modules.id == module_id)
        query.execute()
        return {'status' : 200,  'message' : 'Module successfully deleted'}

class ModulePermissionsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('token', type=str, required=True, help='Token is required for authentication')
        super().__init__()

    @utils.security.authentication_required
    def get(self, module_id):
        args = self.reqparse.parse_args()

        # get current user ID
        user_id = utils.security.get_user_id(args['token'])

        # get permission
        query = (database.Permissions.select()
                .join(database.Modules)
                .switch(database.Permissions)
                .join(database.Groups)
                .join(database.Users)
                .where(database.Users.id == user_id, database.Modules.id == module_id))

        if len(query) != 0:

            query = database.Permissions.get(database.Permissions.module_id == module_id)
            return jsonify({'status' : 200,  'data' : model_to_dict(query)})

        response = make_response(
            jsonify(
                {'status' : 100, 'message' : 'You can not get this module'}
            ),
            403,
        )
        return response

api.add_resource(ModulesListsAPI, '/1.0/modules')
api.add_resource(ModuleAPI, '/1.0/modules/<string:module_id>')
api.add_resource(ModulePermissionsAPI, '/1.0/modules/<string:module_id>/permissions')
#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *


class ConfigurationsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument(
            'value', type=str, help="Value for edit configuration")
        super().__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/configurations')
    def get(self, name):
        try:

            data = database.ApiConfigurations.get(
                database.ApiConfigurations.name == name)

            if data:
                return jsonify({'status': 200, 'data': model_to_dict(data)})

        except DoesNotExist:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Configuration not found'}
                ),
                404,
            )
        return response

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/configurations')
    def put(self, name):
        args = self.reqparse.parse_args()

        query = database.ApiConfigurations.update(
            {
                database.ApiConfigurations.value: args['value']}).where(
            database.ApiConfigurations.name == name)
        query.execute()

        return {'status': 200, 'message': "Configuration successfully updated"}


api.add_resource(ConfigurationsAPI, '/1.0/configurations/<string:name>')

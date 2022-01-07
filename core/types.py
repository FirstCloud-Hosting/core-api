#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *

class ModulesTypesListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('token', type=str, required=True, help='Token is required for authentication')
        super(ModulesTypesListAPI, self).__init__()

    @utils.security.authentication_required
    def get(self):

        #Get all types
        query = database.Types.select().order_by(database.Types.name)
        query = [model_to_dict(item) for item in query]
        data = json.dumps(query, cls=database.JSONEncoder)
        return jsonify({'status' : 200,  'data' : query})

api.add_resource(ModulesTypesListAPI, '/1.0/modules/types')

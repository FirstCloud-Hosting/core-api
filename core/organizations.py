#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *

class OrganizationsListsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('token', type=str, required=True, help='Token is required for authentication')
        super(OrganizationsListsAPI, self).__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/organizations')
    def get(self):

        #Get all organizations
        query = database.Organizations.select()

        query = [model_to_dict(item) for item in query]
        data = json.dumps(query, cls=database.JSONEncoder)
        return jsonify({'status' : 200,  'data' : query})

class OrganizationsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('token', type=str, required=True, help='Token is required for authentication')
        self.reqparse.add_argument('passwordHardening', type=int, default=0, help='Token is required for authentication')
        super(OrganizationsAPI, self).__init__()

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/organizations')
    def get(self, organization_id):
        try:
            #Get an organization
            query = database.Organizations.get(database.Organizations.id == organization_id)
            return jsonify({'status' : 200,  'data' : model_to_dict(query)})

        except DoesNotExist:
            response = make_response(
                jsonify(
                    {'status' : 100, 'message' : 'Organization not found'}
                ),
                404,
            )
            return response

    @utils.security.authentication_required
    @utils.security.allowed_permissions(module='core/organizations')
    def put(self, organization_id):
        args = self.reqparse.parse_args()

        query = database.ApiConfigurations.update({database.Organizations.passwordHardening:args['passwordHardening']}).where(database.ApiConfigurations.id == organization_id)
        query.execute()

        return {'status' : 200,  'message' : "Organization successfully updated"}


api.add_resource(OrganizationsListsAPI, '/1.0/organizations')
api.add_resource(OrganizationsAPI, '/1.0/organizations/<string:organization_id>')

#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *

class AppKeysListsAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('token', type=str, required=True, help='Token is required for authentication')
    super(AppKeysListsAPI, self).__init__()

  @utils.security.authentication_required
  def get(self):
    args = self.reqparse.parse_args()

    #get current user ID
    user_id = utils.security.get_user_id(args['token'])

    #Get all applications keys for user
    query = (database.AppKeys.select()
            .where(database.AppKeys.user_id  == user_id))

    query = [model_to_dict(item) for item in query]
    data = json.dumps(query, cls=database.JSONEncoder)
    return jsonify({'status' : 200,  'data' : query})

  @utils.security.authentication_required
  def post(self):
    args = self.reqparse.parse_args()

    #get current user ID
    user_id = utils.security.get_user_id(args['token'])

    group = database.AppKeys.create(user_id=user_id)

    return jsonify({'status' : 200,  'message' : 'Application Key successfully added', 'id' : group.id})

class AppKeysAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('token', type=str, required=True, help='Token is required for authentication')
    self.reqparse.add_argument('description', type=str, help='Description of your application')
    super(AppKeysAPI, self).__init__()

  @utils.security.authentication_required
  def get(self, appKey_id):
    args = self.reqparse.parse_args()

    #get current user ID
    user_id = utils.security.get_user_id(args['token'])

    query = database.AppKeys.get(database.AppKeys.id == appKey_id, database.AppKeys.user_id == user_id)
    return jsonify({'status' : 200,  'data' : model_to_dict(query)})

  @utils.security.authentication_required
  def put(self, appKey_id):
    args = self.reqparse.parse_args()

    #get current user ID
    user_id = utils.security.get_user_id(args['token'])

    #update group
    query = database.AppKeys.update(description=args['description']).where(database.AppKeys.id == appKey_id, database.AppKeys.user_id == user_id)
    query.execute()
    return {'status' : 200, 'message' : 'Application Key successfully edited'}

  @utils.security.authentication_required
  def delete(self, appKey_id):
    args = self.reqparse.parse_args()

    #get current user ID
    user_id = utils.security.get_user_id(args['token'])

    #delete group
    query = database.AppKeys.delete().where(database.AppKeys.id == appKey_id, database.AppKeys.user_id == user_id)
    query.execute()
    return {'status' : 200,  'message' : 'Application Key successfully deleted'}

api.add_resource(AppKeysListsAPI, '/1.0/appKeys')
api.add_resource(AppKeysAPI, '/1.0/appKeys/<string:appKey_id>')
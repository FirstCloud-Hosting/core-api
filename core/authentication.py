#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *

#Authentication for user
class AuthenticateUserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('token', type=str, help="Token for Authentication")
        self.reqparse.add_argument('email', type=str, help='Email for Authentication')
        self.reqparse.add_argument('password', type=str, help='Password for Authentication')
        self.reqparse.add_argument('X-Forwarded-For', location='headers')
        super(AuthenticateUserAPI, self).__init__()

    @utils.security.authentication_required
    def get(self):
        args = self.reqparse.parse_args()

        return jsonify({'status':200, 'data':  {'user_id' : utils.security.get_user_id(args['token'])} })

    def post(self):
          args = self.reqparse.parse_args()

          if args['X-Forwarded-For'] != None:
              remote_ip = args['X-Forwarded-For']
          else:
              remote_ip = utils.security.get_ip()

          #get hash of password
          hash = utils.cryptography.hash_password( args['password'] )

          try:
              #authentication by email
              if not 'email' in args or args['email'] == None:
	                response = make_response(
	                    jsonify(
	                        {'status' : 100, 'message' : 'Invalid email address'}
	                    ),
	                    403,
	                )
	                return response

              user = database.Users.get(database.Users.email == args['email'], database.Users.password == hash )

              if user:
                  #create session
                  s = Serializer(app.config['SECRET_KEY'], expires_in=int(config['DEFAULT']['SESSION_LIFETIME']))
                  token = s.dumps( { 'id': str(user.id) } ).decode()

                  #log activity
                  database.ActivityLogs.create(activity="Autentication", result="%s : Authentication success" % args['email'])

                  return jsonify({'status': 200, 'data' : {'token' : token, 'user_id' : user.id, 'group_id' : user.group_id, 'expiration' : int(config['DEFAULT']['SESSION_LIFETIME'])} })

              else:
                  response = make_response(
                      jsonify(
                          {'status' : 100, 'message' : 'Authentication failure'}
                      ),
                      403,
                  )
                  return response

          except DoesNotExist:

              #log activity
              database.ActivityLogs.create(activity="Autentication", result="%s : Authentication failure" % args['email'])

              response = make_response(
                  jsonify(
                      {'status' : 100, 'message' : 'Authentication failure'}
                  ),
                  403,
              )
              return response

api.add_resource(AuthenticateUserAPI, '/1.0/authentication')


#Authentication for application
class AuthenticateAppAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('token', type=str, help="Token for Authentication")
        self.reqparse.add_argument('organizationKey', type=str, help='Organization Key for Authentication')
        self.reqparse.add_argument('secretKey', type=str, help='Secret Key for Authentication')
        self.reqparse.add_argument('X-Forwarded-For', location='headers')
        super(AuthenticateAppAPI, self).__init__()

    @utils.security.authentication_required
    def get(self):
        args = self.reqparse.parse_args()

        return jsonify({'status':200, 'data':  {'user_id' : utils.security.get_user_id(args['token'])} })

    def post(self):
          args = self.reqparse.parse_args()

          if args['X-Forwarded-For'] != None:
              remote_ip = args['X-Forwarded-For']
          else:
              remote_ip = get_ip()

          try:
              #get user
              if 'organizationKey' in args and args['organizationKey'] != None and 'secretKey' in args and args['secretKey'] != None:
                  user = (database.AppKeys.select()
                        .join(database.Users)
                        .where(database.Users.organization_id == args['organizationKey'], database.AppKeys.secretKey == args['secretKey']))

              print(user[0].user.__dict__, flush=True)

              if user:
                  #create session
                  s = Serializer(app.config['SECRET_KEY'], expires_in=int(config['DEFAULT']['SESSION_LIFETIME']))
                  token = s.dumps( { 'id': str(user[0].user_id) } ).decode()

                  #log activity
                  database.ActivityLogs.create(activity="Autentication", result="%s - %s : Application authentication success" % (args['organizationKey'], args['secretKey']))

                  return jsonify({'status': 200, 'data' : {'token' : token, 'user_id' : user[0].user_id, 'group_id' : user[0].user.group_id, 'expiration' : int(config['DEFAULT']['SESSION_LIFETIME'])} })

              else:
                  response = make_response(
                      jsonify(
                          {'status' : 100, 'message' : 'Application authentication failure'}
                      ),
                      403,
                  )
                  return response

          except DoesNotExist:

              #log activity
              database.ActivityLogs.create(activity="Autentication", result="%s - %s : Application authentication failure" % (args['organizationKey'], args['secretKey']))

              response = make_response(
                  jsonify(
                      {'status' : 100, 'message' : 'Application authentication failure'}
                  ),
                  403,
              )
              return response

api.add_resource(AuthenticateAppAPI, '/1.0/authenticationApp')

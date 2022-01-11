#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *


class LanguagesListsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument('name', type=str, help='Language name')
        self.reqparse.add_argument('code', type=str, help='Language code')
        super().__init__()

    def get(self):

        # Get all countries
        query = database.Languages.select().order_by(database.Languages.name)
        query = [model_to_dict(item) for item in query]
        return jsonify({'status': 200, 'data': query})

    def post(self):
        args = self.reqparse.parse_args()

        if args['name'] == '' or args['code'] == '':
            return {'status': 100, 'message': 'Cannot create language'}

        try:
            # get if language exist
            module = database.Languages.get(
                database.Languages.code == args['code'])

            if module:
                return {'status': 100, 'message': 'This language already exist'}

        except DoesNotExist:
            language = database.Languages.create(
                name=args['name'], code=args['code'])

            return jsonify({'status': 200,
                            'message': 'Language successfully added',
                            'id': language.id})

        return {'status': 100, 'message': 'Cannot create language'}


class LanguagesAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token',
            type=str,
            required=True,
            help='Token is required for authentication')
        self.reqparse.add_argument('name', type=str, help='Language name')
        self.reqparse.add_argument('code', type=str, help='Language code')
        super().__init__()

    def get(self, language_id):

        try:
            # Get one country
            query = database.Languages.get(
                database.Languages.id == language_id)
            return jsonify({'status': 200, 'data': model_to_dict(query)})

        except DoesNotExist:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Languages not found'}
                ),
                404,
            )
            return response

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/languages')
    def put(self, language_id):
        args = self.reqparse.parse_args()

        if args['name'] == '' or args['code'] == '':
            return {'status': 100, 'message': 'Cannot edit language'}

        # update language
        query = database.Languages.update(
            name=args['name'], code=args['code']).where(
            database.Languages.id == language_id)
        query.execute()
        return {'status': 200, 'message': 'Language successfully edited'}

    @utils.security.authentication_required
    @utils.security.allowed_permissions('core/languages')
    def delete(self, language_id):
        # delete module
        query = database.Languages.delete().where(database.Languages.id == language_id)
        query.execute()
        return {'status': 200, 'message': 'Language successfully deleted'}


api.add_resource(LanguagesListsAPI, '/1.0/languages')
api.add_resource(LanguagesAPI, '/1.0/languages/<string:language_id>')

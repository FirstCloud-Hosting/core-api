#!flask/bin/python
# -*- coding: utf-8 -*-

from common import *

class CountriesListsAPI(Resource):
    def __init__(self):
        super(CountriesListsAPI, self).__init__()

    def get(self):

        #Get all countries
        query = database.Countries.select().order_by(database.Countries.name)
        query = [model_to_dict(item) for item in query]
        data = json.dumps(query, cls=database.JSONEncoder)
        return jsonify({'status' : 200,  'data' : query})


class CountriesAPI(Resource):
    def __init__(self):
        super(CountriesAPI, self).__init__()

    def get(self, code):

        try:
            #Get one country
            query = database.Countries.get(database.Countries.code == code)
            return jsonify({'status' : 200,  'data' : model_to_dict(query)})

        except DoesNotExist:
            response = make_response(
                jsonify(
                    {'status' : 100, 'message' : 'Country not found'}
                ),
                404,
            )
            return response


api.add_resource(CountriesListsAPI, '/1.0/countries')
api.add_resource(CountriesAPI, '/1.0/countries/<string:code>')

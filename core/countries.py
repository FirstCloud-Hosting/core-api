#!flask/bin/python
# -*- coding: utf-8 -*-
"""Countries module allows to manipulate countries data
"""

from common import *


class CountriesListsAPI(Resource):

    """List all countries
    """

    def get(self):
        """Get all countries

        Returns:
            dict: all countries
        """
        # Get all countries
        query = database.Countries.select().order_by(database.Countries.name)
        query = [model_to_dict(item) for item in query]
        return jsonify({'status': 200, 'data': query})


class CountriesAPI(Resource):

    """Manipulate selected country
    """

    def get(self, code):
        """Get name of selected country by country code

        Args:
            code (str): Country code (ISO format)

        Returns:
            dict: informations of selected country
        """
        try:
            # Get one country
            query = database.Countries.get(database.Countries.code == code)
            return jsonify({'status': 200, 'data': model_to_dict(query)})

        except DoesNotExist:
            response = make_response(
                jsonify(
                    {'status': 100, 'message': 'Country not found'}
                ),
                404,
            )
            return response


api.add_resource(CountriesListsAPI, '/1.0/countries')
api.add_resource(CountriesAPI, '/1.0/countries/<string:code>')

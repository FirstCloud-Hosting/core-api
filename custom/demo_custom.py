#!flask/bin/python
# -*- coding: utf-8 -*-
"""Demo_custom is sample of module
"""

from common import *


def register_database():
    """Allows to register classes on database and insert data
    """

    # database.ApiConfigurations.get_or_create(name="price", value="7.99")
    # database.ApiConfigurations.get_or_create(name="freeServers", value="1")
    return True


def register_endpoint():
    """Allows to register endpoints on api
    """

    # api.add_resource(AppKeysListsAPI, '/1.0/demo')
    return True

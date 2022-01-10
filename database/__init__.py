#!flask/bin/python
# -*- coding: utf-8 -*-

# standard modules
import json
from uuid import UUID
import datetime
import os

# core libs
from .tables import *
import utils.configuration
import utils.cryptography


def initialization(
        database_module,
        user,
        passwd,
        db,
        host='localhost',
        port=3306):
    try:
        DB.init(db, user=user, passwd=passwd, host=host, port=port,
                charset="utf8")  # Actually init the database
        DB.connect()
        return True
    except OperationalError as error:
        print(error, flush=True)
        return False


def make_tables():
    """Make the tables in the database"""
    DB.create_tables([Types,
                      Modules,
                      Organizations,
                      Groups,
                      Permissions,
                      Languages,
                      Users,
                      AppKeys,
                      Countries,
                      ApiConfigurations,
                      ActivityLogs])

    # import types list
    with open('%s/data/types.json' % (os.path.split(__file__)[0], ), 'r') as f:
        types = json.load(f)
        for type in types:
            Types.get_or_create(name=type['name'], icon=type['icon'])

    # import languages list
    with open('%s/data/languages.json' % (os.path.split(__file__)[0], ), 'r') as f:
        languages = json.load(f)
        for language in languages:
            Languages.get_or_create(
                name=language['name'],
                code=language['code'])

    # import countries list
    with open('%s/data/countries.json' % (os.path.split(__file__)[0], ), 'r') as f:
        countries = json.load(f)
        for country in countries:
            Countries.get_or_create(name=country['name'], code=country['code'])

    # import modules list
    with open('%s/data/modules.json' % (os.path.split(__file__)[0], ), 'r') as f:
        modules = json.load(f)
        for module in modules:
            type = Types.get(Types.name == module['type'])
            Modules.get_or_create(type_id=type,
                                  name=module['name'],
                                  page=module['page'],
                                  forAdmin=module['forAdmin'])

    # create first organization
    if Organizations.select().count() == 0:
        # create first organization
        organization_id = Organizations.create()

        # create first group
        group_id = Groups.create(organization_id=organization_id,
                                 name="Super-Administrators",
                                 note="Super-Administrators")

        # set permissions for new group
        modules = Modules.select()
        for module in modules:
            Permissions.create(group=group_id,
                               module=module.id,
                               view=1,
                               creation=1,
                               edition=1,
                               deletion=1)

        # get English language id
        language_id = Languages.get(Languages.name == "English")

        # create first user
        Users.create(
            organization_id=organization_id,
            group_id=group_id,
            password=utils.cryptography.hash_password("Administrator"),
            email="administrator@linufy",
            language_id=language_id,
            status=1)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of string
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            # if the obj is datetime, we simply return the value of string
            return str(obj)
        return json.JSONEncoder.default(self, obj)

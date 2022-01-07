#!flask/bin/python
#-*- coding: utf-8 -*-

import sys
sys.dont_write_bytecode = True

from common import *

#Import core modules
import core.configurations
import core.countries
import core.languages
import core.authentication
import core.organizations
import core.types
import core.modules
import core.groups
import core.permissions
import core.appKeys
import core.users
#API Publique

#Import custom modules
import os
import importlib

for module in os.listdir(os.getcwd() + '/custom'):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    handle = importlib.import_module('custom.' + module[:-3])
    try:
        handle.register_database()
    except:
        pass

    try:
        handle.register_endpoint()
    except:
        pass

if __name__ == '__main__':
    if (config['DEFAULT']['ENVIRONMENT']).lower() == "devel":
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    else:
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)

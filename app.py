#!flask/bin/python
# -*- coding: utf-8 -*-

import importlib
import os
import sys
sys.dont_write_bytecode = True

import core.users
import core.appKeys
import core.permissions
import core.groups
import core.modules
import core.types
import core.organizations
import core.authentication
import core.languages
import core.countries
import core.configurations
from common import *

for module in os.listdir(os.getcwd() + '/custom'):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    handle = importlib.import_module('custom.' + module[:-3])
    try:
        handle.register_database()
    except BaseException:
        pass

    try:
        handle.register_endpoint()
    except BaseException:
        pass

if __name__ == '__main__':
    if (config['DEFAULT']['ENVIRONMENT']).lower() == "devel":
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    else:
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)

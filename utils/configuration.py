#!flask/bin/python
# -*- coding: utf-8 -*-

import configparser
import os


def load():
    config = configparser.ConfigParser()
    config.read('%s/../config/config.ini' % os.path.split(__file__)[0])
    return config

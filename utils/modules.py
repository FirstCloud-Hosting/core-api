#!flask/bin/python
# -*- coding: utf-8 -*-

import os


def load(folder):

    for module in os.listdir('%s/../%s' %
                             (os.path.split(__file__)[0], folder)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        __import__(module[:-3], locals(), globals())

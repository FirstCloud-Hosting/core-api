#!flask/bin/python

import sys
import os
sys.dont_write_bytecode = True
sys.path.insert(0, '/var/www/app')
from app import app as application

#activate_this = '/home/gabi/proyectos/WebApps/test/testenv/bin/activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))

import os
import sys

ARDULAB_DIR = os.path.dirname(__file__)
if ARDULAB_DIR == '':
    ARDULAB_DIR= os.path.abspath('.')

sys.path.insert(0, ARDULAB_DIR)
os.chdir(ARDULAB_DIR)

sys.stdout = open('stdout.txt', 'w', 0)
sys.stderr = open('stderr.txt', 'w', 0)

from app import app as application

import logging
file_handler = logging.FileHandler(filename='logs/errors.log')
file_handler.setLevel(logging.INFO)
application.logger.addHandler(file_handler)

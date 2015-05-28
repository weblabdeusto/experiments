import os
import sys

AQUARIUM_DIR = os.path.dirname(__file__)
if AQUARIUM_DIR == '':
    AQUARIUM_DIR= os.path.abspath('.')

sys.path.insert(0, AQUARIUM_DIR)
os.chdir(AQUARIUM_DIR)

sys.stdout = open('stdout.txt', 'w', 0)
sys.stderr = open('stderr.txt', 'w', 0)

from app import app as application

import logging
file_handler = logging.FileHandler(filename='errors.log')
file_handler.setLevel(logging.INFO)
application.logger.addHandler(file_handler)

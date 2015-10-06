import os
import sys

MICROSCOPE_DIR = os.path.dirname(__file__)
if MICROSCOPE_DIR == '':
    MICROSCOPE_DIR= os.path.abspath('.')

sys.path.insert(0, MICROSCOPE_DIR)
os.chdir(MICROSCOPE_DIR)

sys.stdout = open('stdout.txt', 'w', 0)
sys.stderr = open('stderr.txt', 'w', 0)

from app import app as application

import logging
file_handler = logging.FileHandler(filename='errors.log')
file_handler.setLevel(logging.INFO)
application.logger.addHandler(file_handler)


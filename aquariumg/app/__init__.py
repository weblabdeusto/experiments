import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import basedir, LIGHT_ON_TIME, LIGHT_START_TIME
from .experiments import Aquarium

app = Flask(__name__)
app.config.from_object('config')
#app.config["APLICATION_ROOT"] = "/labs/aquariumg" 
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = ''
aq = Aquarium()


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/aquarium.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('weblab aquarium startup')

from app import views, models


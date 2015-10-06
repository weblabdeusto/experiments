import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import basedir
#from .experiments import Aquarium

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
#aq = Aquarium()


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    try:
        file_handler = RotatingFileHandler('logs/microscope.log', 'a',
                                           1 * 1024 * 1024, 10)
    except:
        f = open(basedir+'logs/microscope.log','w')
        f.write('Log file created')
        f.close()
        file_handler = RotatingFileHandler('logs/microscope.log', 'a',
                                           1 * 1024 * 1024, 10)

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('weblab microscope startup')

from app import views, models


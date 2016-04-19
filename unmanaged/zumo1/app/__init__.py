async_mode = 'eventlet'
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from flask import Flask,Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_socketio import SocketIO
from celery import Celery

app = Flask(__name__)
app.config.from_object('config')

zumo = Blueprint('zumo',
                 __name__,
                 template_folder='templates',
                 static_folder='static')

db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)

socketio = SocketIO(app, async_mode=async_mode)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/zumo1.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('weblab zumo robot startup')

from app import views, models, zumo

app.register_blueprint(zumo, url_prefix='/labs/zumoline')

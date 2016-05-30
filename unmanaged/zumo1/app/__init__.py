async_mode = 'eventlet'
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from flask import Flask,Blueprint
from flask_socketio import SocketIO
from flask_sslify import SSLify

app = Flask(__name__)

app.config.from_object('config')

zumo = Blueprint('zumo',
                 __name__,
                 template_folder='templates',
                 static_folder='static')

weblab = Blueprint("weblab", __name__)
checker = Blueprint("checker", __name__)

socketio = SocketIO(app, async_mode=async_mode, resource = "/labs/zumoline/socket.io")
#sslify = SSLify(app)

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

from app import views, zumo, weblab, checker

app.register_blueprint(zumo, url_prefix='/labs/zumoline')
app.register_blueprint(weblab, url_prefix='/labs/zumoline/weblab')
app.register_blueprint(checker, url_prefix='/checker')


import eventlet

eventlet.monkey_patch()

from flask import Flask,Blueprint
from flask_socketio import SocketIO
import redis
from boardManager import BoardManager
from lineFollowerTools import Chrono
from config import GPIOS

app = Flask(__name__)

app.config.from_object('config')

zumo = Blueprint('zumo',
                 __name__,
                 template_folder='templates',
                 static_folder='static')

weblab = Blueprint("weblab", __name__)
checker = Blueprint("checker", __name__)

socketio = SocketIO(app, async_mode='eventlet', resource = "/labs/zumoline/socket.io")
redisClient = redis.Redis()

board_manager = BoardManager(socketio=socketio,redis=redisClient, gpios=GPIOS)
chrono = Chrono(socketio=socketio,redis=redisClient)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/zumo.log', 'a',
                                       1 * 1024 * 1024, 5)
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

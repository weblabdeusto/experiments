
import eventlet

eventlet.monkey_patch()

from flask import Flask, Blueprint, session, request
from flask_socketio import SocketIO
import redis
from dummy.controller import DummyController
from config import APPLICATION_ROOT

app = Flask(__name__)
app.config.from_object('config')

lab = Blueprint('lab', __name__)
dummy = Blueprint('dummy', __name__)
weblab = Blueprint("weblab", __name__)
checker = Blueprint("errorReporter", __name__)
video = Blueprint("video", __name__)

socketio = SocketIO(app, async_mode='eventlet', resource = APPLICATION_ROOT + "/socket.io")
redisClient = redis.Redis()

controller = DummyController(socketio, redisClient)


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/dummy.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('sessionManager dummy startup')



from babel import Babel

if Babel is None:
    print "Not using Babel. Everything will be in English"
else:
    babel = Babel(app)

    supported_languages = ['en','es']
    supported_languages.extend([translation.language for translation in babel.list_translations()])

    @babel.localeselector
    def get_locale():
        locale = request.args.get('locale', None)
        if locale is None:
            locale = request.accept_languages.best_match(supported_languages)
        if locale is None:
            locale = 'en'
        session['locale'] = locale
        return locale

from app import views
from app.sessionManager import views
from app.errorReporter import views
from app.camera import views
from dummy import views
from app.sockets import views


app.register_blueprint(lab, url_prefix=APPLICATION_ROOT)
app.register_blueprint(dummy, url_prefix=APPLICATION_ROOT+'/controller')
app.register_blueprint(weblab, url_prefix=APPLICATION_ROOT+'/weblab')
app.register_blueprint(checker, url_prefix=APPLICATION_ROOT+'/checker')
app.register_blueprint(video, url_prefix=APPLICATION_ROOT+'/camera')
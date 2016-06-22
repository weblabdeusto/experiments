from flask import Flask, request, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from celery import Celery

app = Flask(__name__)
app.config.from_object('config')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)



if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/ardulab-blocks.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('weblab ardulab blockly startup')

from babel import Babel

if Babel is None:
    print "Not using Babel. Everything will be in English"
else:
    babel = Babel(app)

    supported_languages = ['en','es','eu']
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

from app import views, models

import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

APPLICATION_ROOT="/labs/dummy"

CSRF_ENABLED = True
SECRET_KEY = 'SECRET_PASSWORD_HERE'

SESSION_COOKIE_NAME = 'dummy_cookie'
SESSION_COOKIE_PATH = '/'

WEBLAB_USERNAME = 'weblab_instance_name'
WEBLAB_PASSWORD = 'weblab_password'

CAMERA = 'web_camera'
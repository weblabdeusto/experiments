import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'gO57w=09]SBP:x(<\lP~t>5mD@F;@]8|ZhE<k+B\T|0jD8azhXc.X[GwE}h0x7+0k:G)E%d^-0drgM%sw`fi/_Zle^Jp;*~<t?OV0kICBs-}u\<R,\TI<DCdXJg(DGnt,TwDl@*Ebc{~XO>h,XSq]HX}rL<va"r2Z=2edZl[X_P8v=^PKpbG-g2a1yponhRk]n%l:c7%2.ha:)kEZF[K{=fZ&a.-=*dA&;C5,mS}<e!O>|[^zhOzwl#W'


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True


#uploader config
UPLOAD_FOLDER = basedir+'/app/static/uploads/'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024 * 1000
ALLOWED_EXTENSIONS = ['txt', 'ino', 'cpp', 'h', 'c', 'h']
IGNORED_FILES = ['.gitignore']

#Celery config
CELERY_BROKER_URL = 'redis://localhost:6379/3'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'


#compiler config
BINARY_FOLDER = basedir+'/app/static/binaries/'


#Weblab
LOGIN_URL = ""
BASE_URL = "labs/ardulab/"
CAMERA_ENABLED = False
CAMERA_URL = ""

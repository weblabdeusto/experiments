import os

basedir = os.path.abspath(os.path.dirname(__file__))

APPLICATION_ROOT="/labs/zumoline"

CSRF_ENABLED = True
SECRET_KEY = 'gO57w=09]SBP:x(<\lP~t>5mD@F;@]8|ZhE<k+B\T|0jD8azhXc.X[GwE}h0x7+0k:G)E%d^-0drgM%sw`fi/_Zle^Jp;*~<t?OV0kICBs-}u\<R,\TI<DCdXJg(DGnt,TwDl@*Ebc{~XO>h,XSq]HX}rL<va"r2Z=2edZl[X_P8v=^PKpbG-g2a1yponhRk]n%l:c7%2.ha:)kEZF[K{=fZ&a.-=*dA&;C5,mS}<e!O>|[^zhOzwl#W'


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True


#Ardulab config
ideIP = "192.168.0.2/labs/ardulab"
blocklyIP = "192.168.0.2/labs/ardublocks"

#Weblab
LOGIN_URL = ""
DEBUG = True

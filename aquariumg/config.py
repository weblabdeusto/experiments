import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'gO57w=09]SBP:x(<\lP~t>5mD@F;@]8|ZhE<k+B\T|0jD8azhXc.X[GwE}h0x7+0k:G)E%d^-0drgM%sw`fi/_Zle^Jp;*~<t?OV0kICBs-}u\<R,\TI<DCdXJg(DGnt,TwDl@*Ebc{~XO>h,XSq]HX}rL<va"r2Z=2edZl[X_P8v=^PKpbG-g2a1yponhRk]n%l:c7%2.ha:)kEZF[K{=fZ&a.-=*dA&;C5,mS}<e!O>|[^zhOzwl#W'


#APPLICATION_ROOT='/labs/aquariumg/'
#SERVER_NAME='http://weblab.deusto.es/labs/aquariumg'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


#Pagination
POSTS_PER_PAGE=10

#Aquarium config
LIGHT_ON_TIME = 8
LIGHT_START_TIME = 9
REQUIRED_FEED_LAPSE = 2
REQUIRED_AUTOFEED_LAPSE = 6

#Weblab
LOGIN_URL = "https://weblab.deusto.es/weblab/client/#page=experiment&exp.category=Aquatic%20experiments&exp.name=aquariumg"
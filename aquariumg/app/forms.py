from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class LoginForm(Form):
    name = StringField('name', validators=[DataRequired()])


class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])

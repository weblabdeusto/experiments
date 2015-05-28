from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    name = StringField('name', validators=[DataRequired()])


class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])

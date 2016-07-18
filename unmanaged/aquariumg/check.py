#!flask/bin/python

from app import db,models

users=models.User.query.all()
for user in users:
    print 'User: %s with session_id %s'% (user.nickname,user.session_id)

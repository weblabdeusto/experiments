from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    status = db.Column(db.String(10))
    max_date = db.Column(db.DateTime)
    last_poll = db.Column(db.DateTime)
    back = db.Column(db.String(80))
    session_id = db.Column(db.String(80))
    weblab = db.Column(db.Boolean)
    permission = db.Column(db.Boolean)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)

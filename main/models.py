from main import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Documents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    body = db.Column(db.Text)
    visible = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.Text)
    rating = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'{self.name}, {self.body}, {self.filename}, {self.rating}'


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Integer, default=1)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'{self.rate}, {self.user_id}'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

from app import db, login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    is_professor = db.Column(db.Boolean())

    phone = db.Column(db.Integer)
    wsuID = db.Column(db.Integer)

    gpa = db.Column(db.Float)
    major = db.Column(db.String(20))
    graduation = db.Column(db.DateTime)

    def __repr__(self):
        return '<{} {}-{}>'.format("Professor" if self.is_professor else "Student", self.id, self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
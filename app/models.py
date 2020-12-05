from app import db, login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


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

    if is_professor != True:
        applications = db.relationship('Application', backref='student', lazy='dynamic')  # for the student to know
        experiences = db.relationship('Experience', backref='experience', lazy='dynamic')
    courses = db.relationship('Course', backref='instructor', lazy='dynamic')

    def __repr__(self):
        return '<{} {}-{}>'.format("Professor" if self.is_professor else "Student", self.id, self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(1024))
    professor = db.Column(db.Integer, db.ForeignKey(User.id))
    semester = db.Column(db.String(20))
    year = db.Column(db.Integer)
    position_count = db.Column(db.Integer)
    minimum_gpa = db.Column(db.Float)
    minimum_grade = db.Column(db.String(5))
    prior_experience = db.Column(db.String(1024))

    apps = db.relationship('Application', backref='applicant', lazy='dynamic')  # so the user can see their active apps
    experience = db.relationship('Experience', backref='course', lazy='dynamic')

    def __repr__(self):
        return '<Course {} {} {}>'.format(self.name, self.semester, self.year)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(20))  # semester taken
    year = db.Column(db.Integer)
    grade = db.Column(db.String(5))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    accepted = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # so the student can see active apps
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))  # so the prof can see their active openings


class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    past_ta = db.Column(db.Boolean, default=False)
    grade = db.Column(db.String(5))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

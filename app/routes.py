from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.models import User
from app.forms import LoginForm, RegisterForm

@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration complete')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/professor/register', methods=['GET', 'POST'])
def professor_register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, is_professor=True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration complete')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid credentials')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Welcome')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()

    return redirect(url_for('index'))
from functools import wraps

from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.models import User, Course, Application, Experience
from app.forms import LoginForm, RegisterForm, InfoForm, CreateCourseForm, ApplicationForm, EditCourseForm, ExperienceForm, validGrades
from jinja2 import Environment

e = Environment(extensions=["jinja2.ext.do"])


@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()


def student(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.is_professor:
            return redirect('/')
        return func(*args, **kwargs)

    return decorator


def professor(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not current_user.is_professor:
            return redirect('/')
        return func(*args, **kwargs)

    return decorator


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_professor:
        courses = Course.query.filter_by(professor=current_user.id)
    else:
        courses = Course.query.order_by(Course.year).all()
        # min_grade = 10;
        # for i in range(len(validGrades)):
        # if (validGrades[i]==''):
        #     min_grade = i
        #     break
    return render_template('index.html', user=current_user, courses=courses,grades = validGrades)


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


@app.route('/student/course-info/<int:course_id>', methods=['GET'])
@login_required
@student
def student_course_info(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('student/course_info.html', course=course)

@app.route('/student/application/<int:course_id>', methods=['GET', 'POST'])
@login_required
@student
def student_application(course_id):
    course = Course.query.get_or_404(course_id)
    form = ApplicationForm()
    grades = [ 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F' ]
    validGrades = []
    for g in grades:
        if (g==course.minimum_grade):
            validGrades.append(g)
            break
        validGrades.append(g)
    if form.is_submitted():
        application = Application(semester=form.semester.data, year=form.year.data,
                                  student_id=current_user.id, course_id=course_id, grade=form.grade.data)
        db.session.add(application)
        db.session.commit()
        flash('Application Sent')
        return redirect(url_for('index'))
    return render_template('student/student_application.html', course=course, form=form,gradeSelection = validGrades)

@app.route('/student/active_applications')
@login_required
@student
def active_applications():
    return render_template('student/active_applications.html')

@app.route('/student/withdraw/<int:id>', methods=['GET', 'POST'])
@login_required
@student
def student_withdraw(id):
    application = Application.query.get_or_404(id)
    db.session.delete(application)
    db.session.commit()
    flash('Withdrew Application')
    return redirect(url_for('active_applications'))

@app.route('/student/experience/', methods=['POST', 'GET'])
@login_required
@student
def student_experience():
    courses = Course.query.order_by(Course.name).all()
    return render_template('student/experience.html', courses=courses)

@app.route('/student/experience/<int:id>', methods=['POST', 'GET'])
@login_required
@student
def student_experience_form(id):
    form = ExperienceForm()
    course = Course.query.get_or_404(id)
    if form.validate_on_submit():
        flash("Experience Added")
        experience = Experience(grade=form.grade.data, past_ta = form.past_TA.data, course_id = id, student_id = current_user.id)
        db.session.add(experience)
        db.session.commit()
        return redirect(url_for('student_experience'))
    return render_template('student/experience_form.html', course = course, form = form)

@app.route('/student/experience/delete/<int:id>', methods=['POST', 'GET'])
@login_required
@student
def student_delete_experience(id):
    experience = Experience.query.get_or_404(id)
    db.session.delete(experience)
    db.session.commit()
    return redirect(url_for('student_experience'))

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


@app.route('/professor/courses/create', methods=['GET', 'POST'])
@login_required
@professor
def professor_create_course():
    form = CreateCourseForm()

    if form.validate_on_submit():
        course = Course(name=form.name.data, description=form.description.data,
                        semester=form.semester.data, year=form.year.data, professor=current_user.id,
                        position_count=form.position_count.data, minimum_gpa=form.position_count.data,
                        minimum_grade=form.minimum_grade.data, prior_experience=form.prior_experience.data)
        db.session.add(course)
        db.session.commit()
        flash('Course created')

        return redirect('/')

    return render_template('professor/create_course.html', form=form)


@app.route('/professor/courses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@professor
def professor_edit_course(id):
    course = Course.query.get_or_404(id)
    form = EditCourseForm()

    if form.validate_on_submit():
        if form.name.data:
            course.name = form.name.data
        if form.description.data:
            course.description = form.description.data
        if form.semester.data:
            course.semester = form.semester.data
        if form.year.data:
            course.year = form.year.data
        if form.position_count.data:
            course.position_count = form.position_count.data
        if form.minimum_gpa.data:
            course.minimum_gpa = form.minimum_gpa.data
        if form.minimum_grade.data:
            course.minimum_grade = form.minimum_grade.data
        if form.prior_experience.data:
            course.prior_experience = form.prior_experience.data

        db.session.commit()

        flash('Course edited')
        return redirect('/professor/courses')
    else:
        form.semester.data = course.semester
        form.year.data = str(course.year)
        form.minimum_grade.data = course.minimum_grade

    return render_template('professor/edit_course.html', form=form, course=course)


@app.route('/professor/courses/delete/<int:id>', methods=['GET'])
@login_required
@professor
def professor_delete_course(id):
    course = Course.query.get_or_404(id)

    db.session.delete(course)
    db.session.commit()

    return redirect('/')


@app.route('/professor/applicants/<int:course_id>', methods=['GET'])
@login_required
@professor
def professor_applicants(course_id):
    course = Course.query.get_or_404(course_id)
    applicants = Application.query.filter_by(course_id=course_id)
    return render_template('professor/applicants.html', course=course, applicants=applicants)


@app.route('/professor/courses', methods=['GET'])
@login_required
@professor
def professor_courses():
    courses = db.session.query(Course).filter(current_user.id == Course.professor).all()
    return render_template('professor/courses.html', courses=courses)


@app.route('/professor/application/<int:app_id>', methods=['GET'])
@login_required
@professor
def professor_application(app_id):
    application = Application.query.get_or_404(app_id)
    student = User.query.get_or_404(application.student_id)
    course = Course.query.get_or_404(application.course_id)
    return render_template('professor/student.html', app=application, student=student, course=course)


@app.route('/professor/assign/<int:app_id>', methods=['GET'])
@login_required
@professor
def professor_assign(app_id):
    application = Application.query.get_or_404(app_id)
    course = Course.query.get_or_404(application.course_id)
    accepted_apps = Application.query.filter(
        Application.course_id == application.course_id, Application.accepted == True).all()

    if len(accepted_apps) >= course.position_count:
        flash('All positions already filled!')
    else:
        application.accepted = True
        db.session.commit()
    return redirect('/professor/applicants/{}'.format(course.id))


@app.route('/professor/unassign/<int:app_id>', methods=['GET'])
@login_required
@professor
def professor_unassign(app_id):
    application = Application.query.get_or_404(app_id)
    course = Course.query.get_or_404(application.course_id)

    application.accepted = False
    db.session.commit()
    return redirect('/professor/applicants/{}'.format(course.id))


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


@app.route('/info/', methods=['GET', 'POST'])
@login_required
def info():
    form = InfoForm()
    if form.validate_on_submit():
        flash("Information Saved")
        if form.name.data:
            current_user.name = form.name.data
        if form.phone.data:
            current_user.phone = form.phone.data
        if form.wsuID.data:
            current_user.wsuID = form.wsuID.data
        if form.gpa.data:
            current_user.gpa = form.gpa.data
        if form.major.data:
            current_user.major = form.major.data
        if form.graduation.data:
            current_user.graduation = form.graduation.data
        db.session.commit()
        return redirect(url_for('info'))
    return render_template('info.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()

    return redirect(url_for('index'))

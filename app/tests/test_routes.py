import os
import pytest
from flask_login import login_user, logout_user

from config import basedir
from app import app, db, login
from app.models import User, Course, Application, Experience


@pytest.fixture(scope='module')
def test_client(request):
    app.config.update(
        SECRET_KEY='bad-bad-key',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db') + "?check_same_thread=False",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        DEBUG=True,
        TESTING=True,
    )
    db.init_app(app)

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()
    db.create_all()

    yield testing_client

    db.drop_all()
    ctx.pop()


@pytest.fixture
def init_database(request, test_client):
    # Create the database and the database table
    db.create_all()

    yield  # this is where the testing happens!

    # Drop all database tables
    db.drop_all()


@pytest.fixture
def login_professor(request, test_client, init_database):
    # Create professor user
    user = User(name="Professor", email="professor@wsu.edu", is_professor=True)
    user.set_password("professor123")
    db.session.add(user)
    db.session.commit()

    @login.request_loader
    def user_loader(request):
        return user

    yield  # Perform testing


def test_prof_register_successful(request, test_client, init_database):
    resp = test_client.post('/professor/register',
                            data=dict(name="First Last", email="first.last@wsu.edu", password="fdsa",
                                      confirm_password="fdsa"))
    assert resp.status_code == 302

    users = db.session.query(User).all()
    assert len(users) == 1

    user = users[0]
    assert user.name == "First Last"
    assert user.email == "first.last@wsu.edu"
    assert user.check_password("fdsa")


def test_prof_register_mismatching_password(request, test_client, init_database):
    resp = test_client.post('/professor/register',
                            data=dict(name="First Last", email="first.last@wsu.edu", password="fdsa",
                                      confirm_password="asdf"))
    assert resp.status_code == 200
    assert b"Field must be equal to password" in resp.data

    users = db.session.query(User).all()
    assert len(users) == 0


def test_prof_register_not_wsu_domain(request, test_client, init_database):
    resp = test_client.post('/professor/register',
                            data=dict(name="First Last", email="first.last@washington.edu", password="fdsa",
                                      confirm_password="fdsa"))
    assert resp.status_code == 200
    assert b"Sorry, this application is only available to WSU students and professors" in resp.data

    users = db.session.query(User).all()
    assert len(users) == 0


def test_prof_register_empty_fields(request, test_client, init_database):
    resp = test_client.post('/professor/register',
                            data=dict())
    assert resp.status_code == 200
    assert str(resp.data).count("This field is required") == 4

    users = db.session.query(User).all()
    assert len(users) == 0


def test_prof_edit_info(request, test_client, init_database, login_professor):
    resp = test_client.post('/info/', data=dict(
        name="Mr. Professor", phone="1234567890", wsuID="12345678"
    ))

    user = db.session.query(User).first()
    assert user.name == "Mr. Professor"
    assert user.phone == 1234567890
    assert user.wsuID == 12345678


def test_prof_create_course(request, test_client, init_database, login_professor):
    resp = test_client.post('/professor/courses/create',
                            data=dict(name="CptS 322", description="Desc", semester="Spring", year="2021",
                                      position_count="1", minimum_gpa="3.5", minimum_grade="B-",
                                      prior_experience="Fdsa"))
    assert resp.status_code == 302

    courses = db.session.query(Course).all()
    assert len(courses) == 1


def test_prof_create_course_zero_positions(request, test_client, init_database, login_professor):
    resp = test_client.post('/professor/courses/create',
                            data=dict(name="CptS 322", description="Desc", semester="Spring", year="2021",
                                      position_count="-1", minimum_gpa="3.5", minimum_grade="B-",
                                      prior_experience="Fdsa"))
    assert resp.status_code == 200
    assert b"Number must be at least 1" in resp.data

    courses = db.session.query(Course).all()
    assert len(courses) == 0


def test_prof_delete_course(request, test_client, init_database, login_professor):
    course = Course(name="322", description="", professor=1, semester="Spring", year=2021, position_count=1,
                    minimum_gpa=1.0, minimum_grade='B-', prior_experience="")
    db.session.add(course)
    db.session.commit()

    resp = test_client.get('/professor/courses/delete/1')
    assert resp.status_code == 302

    courses = db.session.query(Course).all()
    assert len(courses) == 0


def test_prof_delete_nonexistent_course(request, test_client, init_database, login_professor):
    resp = test_client.get('/professor/courses/delete/1')
    assert resp.status_code == 404


def test_prof_edit_course(request, test_client, init_database, login_professor):
    course = Course(name="322", description="", professor=1, semester="Spring", year=2021, position_count=1,
                    minimum_gpa=1.0, minimum_grade='B-', prior_experience="")
    db.session.add(course)
    db.session.commit()

    resp = test_client.post('/professor/courses/edit/1', data=dict(
        name='CptS 322', description='This is CptS 322', position_count=3, semester="Spring", year="2021",
        minimum_gpa='3.5', minimum_grade='B', prior_experience="abc123"
    ))
    assert resp.status_code == 302

    updated_course = db.session.query(Course).first()
    assert updated_course.name == "CptS 322"
    assert updated_course.description == "This is CptS 322"

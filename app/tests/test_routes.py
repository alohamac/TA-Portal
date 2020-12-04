import os
import pytest
from config import basedir
from app import app, db, login
from app.models import User, Course, Application, Experience


@pytest.fixture(scope='module')
def test_client(request):
    app.config.update(
        SECRET_KEY='bad-bad-key',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
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


def test_prof_register_successful(request, test_client, init_database):
    resp = test_client.post('/professor/register',
                            data=dict(name="First Last", email="first.last@wsu.edu", password="fdsa",
                                      confirm_password="fdsa"))
    assert resp.status_code == 302

    users = db.session.query(User).all()
    assert len(users) == 1


def test_prof_register_mismatching_password(request, test_client, init_database):
    resp = test_client.post('/professor/register',
                            data=dict(name="First Last", email="first.last@wsu.edu", password="fdsa",
                                      confirm_password="asdf"))
    assert resp.status_code == 200

    users = db.session.query(User).all()
    assert len(users) == 0

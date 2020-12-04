import os
import tempfile
import pytest
from config import basedir
from app import app,db,login
from app.models import User,Course,Application,Experience


@pytest.fixture(scope='module')
def test_client(request):
    app.config.update(
        SECRET_KEY = 'bad-bad-key',
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        WTF_CSRF_ENABLED = False,
        DEBUG = True,
        TESTING = True,
    )
    db.init_app(app)
    
    testing_client = app.test_client()
 
    ctx = app.app_context()
    ctx.push()
 
    yield  testing_client 
    ctx.pop()
    
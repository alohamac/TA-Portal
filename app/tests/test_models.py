import datetime
import unittest
from app import app, db
from app.models import User, Course, Application, Experience


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(name='First Last', is_professor=False, email='first.last@wsu.edu')
        u.set_password('password123')  # very secure

        db.session.add(u)
        db.session.commit()

        qu = db.session.query(User).first()

        self.assertFalse(qu.check_password('not password123'))
        self.assertTrue(qu.check_password('password123'))

class CourseModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_course_owner(self):
        u = User(name='Prof', is_professor=True, email='prof@wsu.edu')
        db.session.add(u)
        db.session.commit()

        c = Course(name='322', description='322', professor=u.id)
        db.session.add(c)
        db.session.commit()

        qc = db.session.query(Course).first()

        self.assertEqual(qc.professor, u.id)


class ApplicationModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_course_owner(self):
        p = User(name='Prof', is_professor=True, email='prof@wsu.edu')
        s = User(name='Student', is_professor=False, email='student@wsu.edu')
        db.session.add(p)
        db.session.add(s)
        db.session.commit()

        c = Course(name='322', description='322', professor=p.id)
        db.session.add(c)
        db.session.commit()

        a = Application(semester='Spring', year=2000, grade='A', timestamp=datetime.datetime.now(), accepted=False,
                        student_id=s.id, course_id=c.id)
        db.session.add(a)
        db.session.commit()

        qa = db.session.query(Application).first()
        self.assertEqual(qa.course_id, c.id)
        self.assertEqual(qa.student_id, s.id)

class ExperienceModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_experience_owner(self):
        p = User(name='Prof', is_professor=True, email='prof@wsu.edu')
        s = User(name='Student', is_professor=False, email='student@wsu.edu')
        db.session.add(p)
        db.session.add(s)
        db.session.commit()

        c = Course(name='322', description='322', professor=p.id)
        db.session.add(c)
        db.session.commit()

        e = Experience(past_ta=True,grade="A",student_id=s.id,course_id=c.id)
        db.session.add(e)
        db.session.commit()

        qe = db.session.query(Experience).first()
        self.assertEqual(qe.student_id,s.id)
        self.assertEqual(qe.course_id,c.id)
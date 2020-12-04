from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, PasswordField, BooleanField, IntegerField,\
    DecimalField, DateField
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Length, Email, EqualTo, Optional

from app.models import User

validYears = [
    '2020',
    '2021',
    '2022',
    '2023',
    '2024',
    '2025',
    '2026',
    '2027',
    '2028',
    '2029'
]

validPastYears = [
    '2013',
    '2014',
    '2015',
    '2016',
    '2017',
    '2018',
    '2019',
    '2020'
]

validSemesters = [
    'Spring',
    'Summer',
    'Fall'
]

validGrades = [
    'A',
    'A-',
    'B+',
    'B',
    'B-',
    'C+',
    'C',
    'C-',
    'D+',
    'D',
    'F'
]

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is already in use. Forgot password?')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class InfoForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=70)])
    phone = IntegerField('Phone', validators=[Optional()])
    wsuID = StringField('WSU ID', validators=[Length(max=8)])

    # additional information (students only)
    gpa = DecimalField('GPA',validators=[Optional()])
    major = StringField('Major', validators=[Optional()])
    graduation = DateField('Expected Graduation', format='%m/%Y', validators=[Optional()])
    submit = SubmitField('Save')


class CreateCourseForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=64), DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=1024), DataRequired()])
    semester = SelectField('Semester', choices=validSemesters, validators=[DataRequired()])
    year = SelectField('Year', choices=validYears)
    position_count = IntegerField('Position Count', validators=[DataRequired()])
    minimum_gpa = DecimalField('Minimum GPA', validators=[DataRequired()], places=2)
    minimum_grade = SelectField('Minimum Grade', choices=validGrades, validators=[DataRequired()])
    prior_experience = TextAreaField('Prior Experience', validators=[Length(max=1024), DataRequired()])
    submit = SubmitField('Submit')


class EditCourseForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=64)])
    description = TextAreaField('Description', validators=[Length(max=1024)])
    semester = SelectField('Semester', choices=validSemesters)
    year = SelectField('Year', choices=validYears)
    position_count = IntegerField('Position Count', validators=[Optional()])
    minimum_gpa = DecimalField('Minimum GPA', places=2, validators=[Optional()])
    minimum_grade = SelectField('Minimum Grade', choices=validGrades)
    prior_experience = TextAreaField('Prior Experience', validators=[Length(max=1024)])
    submit = SubmitField('Submit')


class ApplicationForm(FlaskForm):
    gradeSelection=[]
    semester = SelectField('Semester Taken', choices=validSemesters, validators=[DataRequired()])
    year = SelectField('Year Taken', choices=validPastYears, validators=[DataRequired()])
    grade = SelectField('Grade received', choices=gradeSelection)
    submit = SubmitField('Apply')

class ExperienceForm(FlaskForm):
    grade = SelectField('Grade received', choices=validGrades, validators=[DataRequired()])
    past_TA = BooleanField('Previously a TA for this class?')
    submit = SubmitField('Submit')
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, PasswordField, BooleanField, IntegerField, DecimalField, DateField
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Length, Email, EqualTo, Optional
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

from app import db
from app.models import User

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
    email = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

class InfoForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=70)])
    phone = IntegerField('Phone', validators=[Optional()])
    wsuID = StringField('WSU ID',validators=[Length(max =8)])

    #additional information (students only)
    gpa = DecimalField('GPA',validators=[Optional()])
    major = StringField('Major', validators=[Optional()])
    graduation = DateField('Expected Graduation', format ='%m/%Y', validators=[Optional()])
    submit = SubmitField('Save')
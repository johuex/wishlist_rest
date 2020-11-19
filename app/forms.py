'''модуль для хранения классов веб-форм'''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User
import connectDB as cn


class LoginForm(FlaskForm):
    nickname = StringField('Your nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    name = StringField('First Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    phone_number = StringField('Phone number', validators=[DataRequired()])  # TODO кастомный валидатор
    birthday = StringField('Birthday', validators=[DataRequired()])  # TODO кастомный валидатор
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, nickname):
        # TODO переделать в SQL логику
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM 'users' WHERE 'nickname' = (%s);"
        curs.execute(sql, (nickname.data))
        result = curs.fetchone()
        conn.close()
        if result is None:
            user = None
        else:
            user = User(result['user_ID'], result['phone_number'], result['name'], result['surname'], result['userpic'],
                        result['about'], result['birthday'], result['password_hash'], result['nickname'])
        #user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This nickname is occupied.')

    def validate_email(self, email):
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE 'email' = (%s);"
        curs.execute(sql, (email.data))
        result = curs.fetchone()
        conn.close()
        if result is None:
            user = None
        else:
            user = User(result['user_ID'], result['phone_number'], result['name'], result['surname'], result['userpic'],
                        result['about'], result['birthday'], result['password_hash'], result['nickname'])
        #user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('User with this email is already registered.')

import datetime

import phonenumbers
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

import connectDB as cn


class LoginForm(FlaskForm):
    """форма авторизации"""
    nickname = StringField('Your nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """форма регистрации"""
    name = StringField('First Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    phone_number = StringField('Phone number', validators=[DataRequired()])
    birthday = StringField('Birthday', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_nickname(self, nickname):
        """проверка nickname на повтор"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE nickname = %s;"
        curs.execute(sql, (nickname.data,))
        result = curs.fetchone()
        conn.close()
        #user = User.query.filter_by(username=username.data).first()
        if result is not None:
            raise ValidationError('This nickname is occupied.')

    def validate_phone(self, phone_number):
        """проверка номера на существование"""
        try:
            p = phonenumbers.parse(phone_number.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

    def validate_birthday(self, birthday):
        """проверка формата введенного ДР"""
        format_date = "%d/%m/%Y"
        try:
            datetime.datetime.strptime(birthday.data, format_date)
        except ValueError:
            raise ValidationError('Enter your birthday like 31(day)/1(month)/1999(year)')

    def validate_email(self, email):
        """проверка действительности email"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE email = %s;"
        curs.execute(sql, (email.data,))
        result = curs.fetchone()
        conn.close()
        if result is not None:
            raise ValidationError('User with this email is already registered.')


class ChangePasswordForm(FlaskForm):
    """изменение пароля"""
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    newPassword1 = PasswordField('New Password', validators=[DataRequired()])
    newPassword2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('newPassword1')])
    submit = SubmitField('Submit')

    def validate_oldPassword(self, oldPassword):
        """проверка ввода старого пароля"""
        if current_user.check_password(oldPassword.data):
            return
        else:
            raise ValidationError('Old Password is incorrect')
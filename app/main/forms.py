"""модуль для хранения классов веб-форм"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField, \
    SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
import phonenumbers
import datetime
import connectDB as cn
from flask_login import current_user


class EditProfileForm(FlaskForm):
    """форма для изменения данных в профиле"""
    user_name = StringField('Your name', validators=[DataRequired()])
    surname = StringField('Your surname', validators=[DataRequired()])
    nickname = StringField('Your nickname', validators=[DataRequired()])
    birthday = StringField('Birthday', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone_number', validators=[DataRequired()])
    about = TextAreaField('About me', validators=[Length(min=0, max=250)])
    submit = SubmitField('Submit')

    def validate_nickname(self, nickname):
        """проверка nickname на повтор"""
        if current_user.nickname == nickname.data:
            return
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE nickname = %s;"
        curs.execute(sql, (nickname.data,))
        result = curs.fetchone()
        conn.close()
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
        """проверка существования ящика"""
        if current_user.email == email.data:
            return
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE email = %s;"
        curs.execute(sql, (email.data,))
        result = curs.fetchone()
        conn.close()
        if result is not None:
            raise ValidationError('User with this email is already registered.')


class EditWishForm(FlaskForm):
    """форма изменения желания"""
    title = StringField('Title', validators=[DataRequired()])
    about = TextAreaField('Tell something about your wish', validators=[Length(min=0, max=250)])
    access_level = BooleanField('Opened for others', false_values=(False,))
    picture = FileField('Picture')
    degree = SelectField('Degree of wish desire',
                         choices=[(1, 'I really really want it'), (2, 'I really want it'), (3, 'I want it'),
                                  (4, 'I do not really want it'), (5, 'I do not want it')])
    submit = SubmitField('Submit')


class AddWishForm(FlaskForm):
    """форма добавления желания"""
    title = StringField('Title', validators=[DataRequired()])
    about = TextAreaField('Tell something about your wish', validators=[Length(min=0, max=250)])
    access_level = BooleanField('Opened for others', default='checked', false_values=(False,))
    picture = FileField('Picture')
    degree = SelectField('Degree of wish desire', choices=[(1, 'I really really want it'), (2, 'I really want it'), (3, 'I want it'),
                                                           (4, 'I do not really want it'), (5, 'I do not want it')],
                         validate_choice=True)
    submit = SubmitField('Submit')


class AddWishListForm(FlaskForm):
    """форма добавления списка желаний"""
    title = StringField('Title', validators=[DataRequired()])
    about = TextAreaField('Tell something about this list', validators=[Length(min=0, max=250)])
    access_level = BooleanField()
    submit = SubmitField('Submit')
    wishes = SelectMultipleField(
        'Add your already created wishes to the list ', validate_choice=False, coerce=int)  # поле выбора какие желания добавить в списке


class EditWishListForm(FlaskForm):
    """форма изменения списка желаний"""
    title = StringField('Title', validators=[DataRequired()])
    about = TextAreaField('Tell something about this list', validators=[Length(min=0, max=250)])
    access_level = BooleanField()
    submit = SubmitField('Submit')
    wishes = SelectMultipleField(
        'Add your already created wishes to the list ', validate_choice=False, coerce=int)  # поле выбора какие желания добавить в списке

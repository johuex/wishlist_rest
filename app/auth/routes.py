import datetime

from flask import url_for, flash, request, render_template
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
import connectDB as cn
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User
from app.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """функция авторизации"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # во избежание повторной авторизации
    form = LoginForm()
    if form.validate_on_submit():
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE nickname = %s;"
        curs.execute(sql, (form.nickname.data,))
        result = curs.fetchone()
        conn.close()
        if result is None:
            user = None
        else:
            user = User(result['user_id'], result['phone_number'], result['user_name'], result['surname'],
                        result['userpic'],
                        result['about'], result['birthday'], result['password_hash'], result['nickname'],
                        result['email'], result["last_seen"])
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(
                next_page).netloc != '':  # перенаправление на след страницу, если не был авторизован
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    """функция деавторизации"""
    logout_user()
    return redirect(url_for('index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """функция регистрации"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(phone_number=form.phone_number.data, name=form.name.data, surname=form.surname.data,
                    birthday=form.birthday.data, nickname=form.nickname.data, email=form.email.data)
        user.set_password(form.password.data)
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO users (phone_number, username, surname, birthday, \
        password_hash, nickname, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
        curs.execute(sql, (form.phone_number.data, form.name.data, form.surname.data,
                           datetime.datetime.strptime(form.birthday.data, '%d/%m/%Y'),
                           generate_password_hash(form.password.data), form.nickname.data, form.email.data,))
        result = curs.fetchone()
        image_path = 'static/images/users/userpic.png'  # фото по умолчанию
        sql = 'UPDATE users ' \
              'SET userpic = %s ' \
              'WHERE user_id = %s;'
        curs.execute(sql, (image_path, result["user_id"]))
        conn.commit()
        conn.close()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """смена пароля"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.newPassword1.data)
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'UPDATE users ' \
              'SET password_hash = %s ' \
              'WHERE nickname = %s;'
        curs.execute(sql, (current_user.password_hash, current_user.nickname,))
        conn.commit()
        conn.close()
        flash('Your changes have been saved.')
        return redirect(url_for('change_password'))
    return render_template('change_password.html', title='Changing Password',
                           form=form)

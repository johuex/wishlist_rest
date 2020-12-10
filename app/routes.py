"""логика для web-страниц"""
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.urls import url_parse
import connectDB as cn
from app.models import User
import datetime
from PIL import Image
import psycopg2
from io import BytesIO



@app.route('/')
@app.route('/index')
def index():
    """главная страница"""
    """тут будут последние 50 открытых желаний всех пользователей"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM item WHERE access_level = %s LIMIT 50;"
    curs.execute(sql, (True,))
    result = curs.fetchall()
    conn.close()
    return render_template('index.html', wish_item=result)


@app.route('/login', methods=['GET', 'POST'])
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
            user = User(result['user_id'], result['phone_number'], result['user_name'], result['surname'], result['userpic'],
                        result['about'], result['birthday'], result['password_hash'], result['nickname'], result['email'],
                        result["last_seen"])
        #user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':  # перенаправление на след страницу, если не был авторизован
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """функция деавторизации"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        img = open('userpic.jpg', 'rb').read()
        user = User(phone_number=form.phone_number.data, name=form.name.data, surname=form.surname.data,
                    birthday=form.birthday.data, nickname=form.nickname.data, email=form.email.data)
        user.set_password(form.password.data)
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO users (phone_number, user_name, surname, birthday, \
        password_hash, nickname, email, userpic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        curs.execute(sql, (form.phone_number.data, form.name.data, form.surname.data, datetime.datetime.strptime(form.birthday.data, '%d/%m/%Y'),
                           generate_password_hash(form.password.data), form.nickname.data, form.email.data, psycopg2.Binary(img),))
        conn.commit()
        conn.close()
        #user = User(username=form.username.data, email=form.email.data)
        #db.session.add(user)
        #db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.before_request
def before_request():  # выполняется непосредственно перед функцией просмотра
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'UPDATE users SET last_seen = %s WHERE nickname = %s;'
        curs.execute(sql, (current_user.last_seen, current_user.nickname,))
        conn.commit()
        conn.close()


@app.route('/<nickname>')
@login_required
def user_profile(nickname):
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * FROM users WHERE nickname = %s;'
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        user = None
        # TODO вывод об ошибке, что пользователь не найден
    else:
        user = User(result['user_id'], result['phone_number'], result['user_name'], result['surname'], bytes(result['userpic']),
                    result['about'], result['birthday'], result['password_hash'], result['nickname'], result['email'])
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM item WHERE access_level = %s;"
        curs.execute(sql, (True,))
        result = curs.fetchall()
        conn.close()
    return render_template('user_profile.html', user=user, wish_item=result)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # если пользователь изменил информацию и она прошла валидацию, то данные сохраняются и записываются в БД
        current_user.user_name = form.user_name.data
        old_nick = current_user.nickname
        current_user.nickname = form.nickname.data
        current_user.surname = form.surname.data
        current_user.birthday = form.birthday.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        current_user.about = form.about.data
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'UPDATE users ' \
              'SET user_name = %s, surname = %s, birthday = %s,' \
              'email = %s, phone_number = %s, about = %s, nickname = %s ' \
              'WHERE nickname = %s;'
        curs.execute(sql, (form.user_name.data, form.surname.data, datetime.datetime.strptime(form.birthday.data, '%d/%m/%Y'), form.email.data,
                           form.phone_number.data, form.about.data, form.nickname.data, old_nick,))
        conn.commit()
        conn.close()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile', title='Edit Profile',
                        form=form))
    elif request.method == 'GET':
        # если метод GET, то в формы записываем данные пользователя
        form.user_name.data = current_user.user_name
        form.nickname.data = current_user.nickname
        form.surname.data = current_user.surname
        form.birthday.data = current_user.birthday
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.about.data = current_user.about
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
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


@app.errorhandler(404)  # рендер об ошибке 404
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)  # рендер об ошибке 500
def internal_error(error):
    # db.session.rollback() - ???
    return render_template('500.html'), 500


@app.route('/friend_request/<nickname>')
@login_required
def add_friend(nickname):
    #user = User.query.filter_by(username=username).first() # кому посылаем запрос???
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT user_id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None: # если пользователь не найден
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    '''if user == current_user: # самому себе тоже не отправить запрос в друзья
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))'''
    current_user.send_request(result['user_id'])
    #db.session.commit()
    flash('You have send friend request to {}!'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@app.route('/delete_friend/<nickname>')
@login_required
def delete_friend(nickname):
    #user = User.query.filter_by(username=username).first()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT user_id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    '''if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))'''
    current_user.remove_friend(result['user_id'])
    #db.session.commit()
    flash('You and {} are not friends .'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))

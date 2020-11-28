"""логика для web-страниц"""
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import connectDB as cn
from app.models import User
import datetime


@app.route('/')
@app.route('/index')
def index():
    """главная страница"""
    user = {'username': 'Эльдар Рязанов'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)


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
            user = User(result['user_ID'], result['phone_number'], result['name'], result['surname'], result['userpic'],
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
        user = User(phone_number=form.phone_number.data, name=form.name.data, surname=form.surname.data,
                    birthday=form.birthday.data, nickname=form.nickname.data, email=form.email.data)
        user.set_password(form.password.data)
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO users (phone_number, user_name, surname, birthday, \
        password_hash, nickname, email) VALUES (%(str)s, %(str)s, %(str)s, %(date)s, %(str)s, $(str)s, %(str)s);"
        curs.execute(sql, (user.phone_number, user.name, user.surname, datetime.datetime.strptime(user.birthday, '%d/%m/%Y'), user.password_hash,
                           user.nickname, user.email))
        conn.commit()
        conn.close()
        #user = User(username=form.username.data, email=form.email.data)
        #db.session.add(user)
        #db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@login.user_loader
def load_user(user_id):
    """пользовательский загрузчик (связываем Flask-Login и БД)"""
    conn = cn.get_connection()
    cursor = conn.cursor()
    sql = "SELECT 'user_ID' FROM users WHERE 'user_ID' = %(int)s;"
    result = cursor.execute(sql, (int(user_id),))
    cursor.close()
    conn.close()
    return result['user_id']


@app.before_request
def before_request():
    if current_user.is_authenticasted:
        current_user.last_seen = datetime.utcnow()
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "UPDATE users " \
              "SET last_seen = %(datetime)s" \
              "WHERE 'nickname' = %(str)s;"
        curs.execute(sql, (current_user.last_seen, current_user.nickname,))
        conn.commit()
        conn.close()


@app.route('/<nickname>')
@login_required
def user_profile(nickname):
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT * FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        user = None
        # TODO вывод об ошибке, что пользователь не найден
    else:
        user = User(result['user_ID'], result['phone_number'], result['name'], result['surname'], result['userpic'],
                    result['about'], result['birthday'], result['password_hash'], result['nickname'], result['email'])
    return render_template('user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # если пользователь изменил информацию и она прошла валидацию, то данные сохраняются и записываются в БД
        current_user.user_name = form.user_name.data
        current_user.surname = form.surname.data
        current_user.birthday = form.birthday.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        current_user.about = form.about.data
        #db.session.commit()
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "UPDATE users " \
              "SET user_name = %(str)s, surname = %(str)s, birthday = %(date)s," \
              "email = %(str)s, phone_number = %(str)s, about = %(str)s, password_hash = %(str)s" \
              "WHERE 'nickname' = %(str)s;"
        curs.execute(sql, (form.user_name.data, form.surname.data, datetime.datetime.strptime(form.birthday.data, '%d/%m/%Y'), form.email.data,
                           form.phone_number.data, form.about.data))
        conn.commit()
        conn.close()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        # если метод GET, то в формы записываем данные пользователя
        form.user_name.data = current_user.user_name
        form.surname.data = current_user.surname
        form.birthday.data = current_user.birthday
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.about.data = current_user.about
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

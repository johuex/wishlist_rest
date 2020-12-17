"""логика для web-страниц"""
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm, EditWishForm, AddWishForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.urls import url_parse
import connectDB as cn
from app.models import User
import datetime
import psycopg2


@app.route('/')
@app.route('/index')
def index():
    """главная страница"""
    '''тут будут последние 50 открытых желаний всех пользователей'''
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
            user = User(result['user_id'], result['phone_number'], result['user_name'], result['surname'],
                        result['userpic'],
                        result['about'], result['birthday'], result['password_hash'], result['nickname'],
                        result['email'],
                        result["last_seen"])
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


@app.route('/logout')
def logout():
    """функция деавторизации"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """функция регистрации"""
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
        curs.execute(sql, (form.phone_number.data, form.name.data, form.surname.data,
                           datetime.datetime.strptime(form.birthday.data, '%d/%m/%Y'),
                           generate_password_hash(form.password.data), form.nickname.data, form.email.data,
                           psycopg2.Binary(img),))
        conn.commit()
        conn.close()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.before_request
def before_request():  # выполняется непосредственно перед функцией просмотра
    """при каждом запросе авторизованного пользователя записывается его последнее время активности"""
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
    """показ профиля пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * FROM users WHERE nickname = %s;'
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        user = None
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    else:
        user = User(result['user_id'], result['phone_number'], result['user_name'], result['surname'],
                    result['userpic'],
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
    """изменение данных профиля"""
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
        curs.execute(sql, (
        form.user_name.data, form.surname.data, datetime.datetime.strptime(form.birthday.data, '%d/%m/%Y'),
        form.email.data,
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


@app.errorhandler(404)  # рендер об ошибке 404
def not_found_error(error):
    """вывод ошибки 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)  # рендер об ошибке 500
def internal_error(error):
    """вывод ошибки 500"""
    # db.session.rollback() - ???
    return render_template('500.html'), 500


@app.route('/add_request/<nickname>')
@login_required
def add_friend(nickname):
    """добавить пользователя в друзья (отправить запрос на дружбу)"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT user_id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:  # если пользователь не найден
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.send_request(result['user_id'])
    flash('You have send friend request to {}!'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@app.route('/delete_friend/<nickname>')
@login_required
def delete_friend(nickname):
    """удалить пользователя из друзей"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT user_id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.remove_friend(result['user_id'])
    flash('You and {} are not friends .'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@app.route('/cancel_request/<nickname>')
@login_required
def cancel_request(nickname):
    """отменить запрос в друзья"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT user_id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.reject_request(result['user_id'])
    flash('You canceled friend request to {} .'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@app.route('/accept_request/<nickname>')
@login_required
def accept_request(nickname):
    """принять запрос в друзья"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT user_id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.accept_request(result['user_id'])
    flash('You and {} are friends now.'.format(nickname))
    # TODO обновлять страницу на которой находишься, а не кидать на профиль
    #next_page = request.args.get('now')
    return redirect(url_for('user_profile', nickname=nickname))


@app.route('/news')
@login_required
def news():
    """новости от друзей"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = '''SELECT list_id, title, 'list' AS types ''' \
          'FROM wishlist ' \
          'WHERE access_level = %s and user_id IN' \
          '     (SELECT user_id_2' \
          '      FROM friendship' \
          '      WHERE user_id_1 = %s) ' \
          'UNION ' \
          '''SELECT item_id, title, 'wish' AS types ''' \
          'FROM item JOIN user_item USING (item_id) ' \
          'WHERE access_level = %s and user_id IN' \
          '     (SELECT user_id_2 ' \
          '      FROM friendship ' \
          '      WHERE user_id_1 = %s);'
    curs.execute(sql, (True, current_user.user_id, True, current_user.user_id,))
    result = curs.fetchall()
    conn.close()
    return render_template('friend_news.html', wishes=result)


@app.route('/friends')
@login_required
def friends():
    """отображение друзей пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    # запрос на друзей
    sql = 'SELECT user_id, user_name, surname, userpic, nickname ' \
          'FROM users ' \
          'WHERE user_id IN (' \
          'SELECT user_id_2 ' \
          'FROM friendship ' \
          'WHERE user_id_1 = %s);'
    curs.execute(sql, (current_user.user_id,))
    result = curs.fetchall()
    # запрос на запросы-дружбу
    sql = 'SELECT user_name, surname, userpic, nickname ' \
          'FROM users ' \
          'WHERE user_id IN (' \
          'SELECT user_id_from ' \
          'FROM friends_requests ' \
          'WHERE user_id_to = %s);'
    curs.execute(sql, (current_user.user_id,))
    result2 = curs.fetchall()
    conn.close()
    return render_template('friendlist.html', friends=result, requests=result2)


@app.route('/<nickname>/wishes')
@login_required
def all_item(nickname):
    """отображение всех желаний и списков пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    user_id = None
    result = None
    if current_user.nickname == nickname:
        user_id = current_user.user_id
        sql = '''SELECT list_id, title, user_id, 'list' AS types ''' \
              'FROM wishlist ' \
              'WHERE user_id = %s ' \
              'UNION ' \
              '''SELECT item_id, title, user_id, 'wish' AS types ''' \
              'FROM item JOIN user_item USING (item_id) ' \
              'WHERE user_id = %s;'
        curs.execute(sql, (user_id, user_id,))
        result = curs.fetchall()
    else:
        # только открытые списки
        sql = 'SELECT user_id ' \
              'FROM users ' \
              'WHERE nickname = %s;'
        curs.execute(sql, (nickname,))
        user_id = curs.fetchone()
        sql = '''SELECT list_id, title, user_id 'list' AS types ''' \
              'FROM wishlist ' \
              'WHERE user_id = %s AND access_level = %s ' \
              'UNION ' \
              '''SELECT item_id, title, user_id 'wish' AS types ''' \
              'FROM item JOIN user_item  USING (item_id) ' \
              'WHERE user_id = %s AND access_level = %s;'
        curs.execute(sql, (user_id["user_id"], True, user_id["user_id"], True,))
        result = curs.fetchall()
    conn.close()
    return render_template('fullwish.html', wishes=result, nickname=nickname)


@app.route('/presents')
@login_required
def presents():
    """отображение желаний, который будет исполнять пользователь"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT user_id ' \
          'FROM users ' \
          'WHERE nickname = %s;'
    curs.execute(sql, (current_user.nickname,))
    user_id = curs.fetchone()
    sql = 'SELECT item_id, title ' \
          'FROM item ' \
          'WHERE giver_id = %s;'
    curs.execute(sql, (user_id["user_id"],))
    result = curs.fetchall()
    conn.close()
    return render_template('my_presents.html', presents=result)


@app.route('/<item_id>')
def wish_item(item_id):
    """отображение конкретного желания"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * ' \
          'FROM item ' \
          'WHERE item_id = %s);'
    curs.execute(sql, (item_id,))
    result = curs.fetchone()
    conn.close()
    return render_template('show_wish.html', wish=result)


@app.route('/<list_id>')
def wishlist_item(list_id):
    """отображение конкретного списка"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * ' \
          'FROM item ' \
          'WHERE item_id = %s);'
    curs.execute(sql, (list_id,))
    result = curs.fetchone()
    conn.close()
    return render_template('show_list.html', wishlist=result, wish_items=result2)


@app.route('/add_wish')
@login_required
def add_wish():
    """добавить желание"""
    form = AddWishForm()
    if form.validate_on_submit():
        conn = cn.get_connection()
        curs = conn.cursor()
        # заливаем желание
        sql = 'INSERT INTO item (title, about, access_level, picture) VALUES (%s, %s, %s, %s);'
        curs.execute(sql, (form.title.data, form.about.data, form.access_level.data, form.picture.data,))
        # связываем желание и его степень
        sql = ''
        curs.execute(sql)
        result = curs.fetchone()
        sql = 'INSERT INTO item_degree () VALUES (%s, %s)'
        curs.execute(sql, (,))
        conn.commit()
        conn.close()
    return render_template('add_wish.html', form=form)


@app.route('/<item_id>/edit')
@login_required
def edit_wish(item_id):
    """изменение данных желания желания"""
    form = EditWishForm()
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * ' \
          'FROM item ' \
          'WHERE item_id = %s);'
    curs.execute(sql, (item_id,))
    result = curs.fetchall()
    conn.close()
    return render_template('add_wish.html', wish=result, form=form)


@app.route('/<list_id>/edit')
@login_required
def edit_wishlist(list_id):
    """изменение данных желания желания"""

    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * ' \
          'FROM item ' \
          'WHERE item_id = %s);'
    curs.execute(sql, (list_id,))
    result = curs.fetchall()
    conn.close()
    return render_template('add_wish.html', wish=result)


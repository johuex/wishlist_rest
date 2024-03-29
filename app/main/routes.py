"""логика для web-страниц"""

from flask import render_template, flash, redirect, url_for, request
from app.main.forms import EditProfileForm, EditWishForm, AddWishForm, \
    AddWishListForm, EditWishListForm
from flask_login import current_user, login_required
import connectDB as cn
from app.models import User
import datetime
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    """главная страница"""
    '''тут будут последние 50 открытых желаний всех пользователей'''
    conn = cn.get_connection()
    curs = conn.cursor()
    # только открытые списки и открытые желания вне списков
    sql = '''SELECT wishlist.id AS id, title, NULL AS picture, 'list' AS types, users.nickname ''' \
          'FROM wishlist JOIN users USING (id) ' \
          'WHERE wishlist.access_level = %s ' \
          'UNION ' \
          '''SELECT item.id AS id, title, (SELECT path_to_picture FROM item_picture WHERE item_id = item.id), 'wish' AS types, users.nickname ''' \
          'FROM item JOIN user_item ' \
          'ON item.id = user_item.item_id ' \
          'JOIN users ' \
          'ON users.id = user_item.user_id ' \
          'WHERE item.access_level = %s AND item.id NOT IN (SELECT item_id FROM item_list);'
    curs.execute(sql, (0, 0,))
    result = curs.fetchall()
    conn.close()
    return render_template('index.html', wishes=result)


@bp.before_request
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


@bp.route('/<nickname>')
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
        user = User(result['id'], result['phone_number'], result['username'], result['surname'],
                    result['userpic'],
                    result['about'], result['birthday'], result['password_hash'], result['nickname'], result['email'])
    return render_template('user_profile.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
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
              'SET username = %s, surname = %s, birthday = %s,' \
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


@bp.route('/add_request/<nickname>')
@login_required
def add_friend(nickname):
    """добавить пользователя в друзья (отправить запрос на дружбу)"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:  # если пользователь не найден
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.send_request(result['id'])
    flash('You have send friend request to {}!'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@bp.route('/delete_friend/<nickname>')
@login_required
def delete_friend(nickname):
    """удалить пользователя из друзей"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.remove_friend(result['id'])
    flash('You and {} are not friends .'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@bp.route('/cancel_request/<nickname>')
@login_required
def cancel_request(nickname):
    """отменить запрос в друзья"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.reject_request(result['id'])
    flash('You canceled friend request to {} .'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@bp.route('/accept_request/<nickname>')
@login_required
def accept_request(nickname):
    """принять запрос в друзья"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = "SELECT id FROM users WHERE nickname = %s;"
    curs.execute(sql, (nickname,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    current_user.accept_request(result['id'])
    flash('You and {} are friends now.'.format(nickname))
    return redirect(url_for('user_profile', nickname=nickname))


@bp.route('/news')
@login_required
def news():
    """новости от друзей"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = '''SELECT wishlist.id AS id, title, 'list' AS types, NULL AS picture ''' \
          'FROM wishlist ' \
          'WHERE access_level = %s and id IN' \
          '     (SELECT id_2' \
          '      FROM friendship' \
          '      WHERE id_1 = %s) ' \
          'UNION ' \
          '''SELECT item.id AS id, title, 'wish' AS types, picture ''' \
          'FROM item JOIN user_item USING (id) ' \
          'WHERE access_level = %s AND id IN' \
          '     (SELECT id_2 ' \
          '      FROM friendship ' \
          '      WHERE id_1 = %s) AND giver_id IS NULL AND item_id NOT IN (SELECT item_id FROM item_list);'
    curs.execute(sql, (True, current_user.id, True, current_user.id,))
    result = curs.fetchall()
    conn.close()
    return render_template('friend_news.html', wishes=result)


@bp.route('/friends')
@login_required
def friends():
    """отображение друзей пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    # запрос на друзей
    sql = 'SELECT id, user_name, surname, userpic, nickname ' \
          'FROM users ' \
          'WHERE id IN (' \
          'SELECT user_id_2 ' \
          'FROM friendship ' \
          'WHERE user_id_1 = %s);'
    curs.execute(sql, (current_user.id,))
    result = curs.fetchall()
    # запрос на запросы-дружбу
    sql = 'SELECT user_name, surname, userpic, nickname ' \
          'FROM users ' \
          'WHERE id IN (' \
          'SELECT id_from ' \
          'FROM friends_requests ' \
          'WHERE id_to = %s);'
    curs.execute(sql, (current_user.id,))
    result2 = curs.fetchall()
    conn.close()
    return render_template('friendlist.html', friends=result, requests=result2)


@bp.route('/<nickname>/wishes')
@login_required
def all_item(nickname):
    """отображение всех желаний и списков пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    id = None
    result = None
    if current_user.nickname == nickname:
        id = current_user.id
        sql = '''SELECT id AS id, title, id, 'list' AS types, 0 AS giver_id, NULL AS picture ''' \
              'FROM wishlist ' \
              'WHERE id = %s ' \
              'UNION ' \
              '''SELECT item_id AS id, title, id, 'wish' AS types, giver_id, picture ''' \
              'FROM item JOIN user_item USING (item_id) ' \
              'WHERE id = %s AND item_id NOT IN (SELECT item_id FROM item_list);'
        curs.execute(sql, (id, id,))
        result = curs.fetchall()
    else:
        # только открытые списки
        sql = 'SELECT id ' \
              'FROM users ' \
              'WHERE nickname = %s;'
        curs.execute(sql, (nickname,))
        id = curs.fetchone()
        sql = '''SELECT id AS id, title, id, 'list' AS types, 0 AS giver_id, NULL AS picture ''' \
              'FROM wishlist ' \
              'WHERE id = %s AND access_level = %s ' \
              'UNION ' \
              '''SELECT item_id AS id, title, id, 'wish' AS types, giver_id, picture ''' \
              'FROM item JOIN user_item  USING (item_id) ' \
              'WHERE id = %s AND access_level = %s AND giver_id IS NULL AND item_id NOT IN (SELECT item_id FROM item_list);'
        curs.execute(sql, (id["id"], True, id["id"], True,))
        result = curs.fetchall()
    conn.close()
    return render_template('fullwish.html', wishes=result, nickname=nickname)


@bp.route('/presents')
@login_required
def presents():
    """отображение желаний, который будет исполнять пользователь"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT id ' \
          'FROM users ' \
          'WHERE nickname = %s;'
    curs.execute(sql, (current_user.nickname,))
    id = curs.fetchone()
    sql = 'SELECT item_id, title ' \
          'FROM item ' \
          'WHERE giver_id = %s;'
    curs.execute(sql, (id["id"],))
    result = curs.fetchall()
    conn.close()
    return render_template('my_presents.html', presents=result, nickname=current_user.nickname)


@bp.route('/wish/<item_id>')
def wish_item(item_id):
    """отображение конкретного желания"""
    conn = cn.get_connection()
    curs = conn.cursor()
    # все о wish
    sql = 'SELECT * ' \
          'FROM item ' \
          'WHERE id = %s;'
    curs.execute(sql, (item_id,))
    result = curs.fetchone()
    sql = 'SELECT degree ' \
          'FROM degree_of_desire ' \
          'WHERE degree_id IN (' \
          '     SELECT degree_id ' \
          '     FROM item_degree ' \
          '     WHERE id = %s);'
    curs.execute(sql, (result["item_id"],))
    result3 = curs.fetchone()
    # защита от несанкционированного доступа
    sql = 'SELECT nickname ' \
          'FROM users ' \
          'WHERE id IN (' \
          '     SELECT id ' \
          '     FROM user_item ' \
          '     WHERE id = %s);'
    curs.execute(sql, (item_id,))
    result2 = curs.fetchone()
    conn.close()
    if (result["access_level"] and result["giver_id"] is None) or current_user.nickname == result2["nickname"]:
        return render_template('show_wish.html', wish=result, nickname=result2["nickname"], degree=result3["degree"])
    else:
        return render_template('show_wish.html', wish=None, nickname=None, degree=None)


@bp.route('/list/<id>')
def wishlist_item(id):
    """отображение конкретного списка"""
    id = int(id)
    conn = cn.get_connection()
    curs = conn.cursor()
    # информация о списке
    sql = 'SELECT * ' \
          'FROM wishlist ' \
          'WHERE id = %s;'
    curs.execute(sql, (id,))
    result = curs.fetchone()
    # все желания в данном списке
    sql = 'SELECT * ' \
          'FROM item ' \
          'WHERE id IN (SELECT item_id FROM item_list WHERE id = %s)'
    curs.execute(sql, (id,))
    result2 = curs.fetchall()
    conn.close()
    return render_template('show_list.html', wishlist=result, wish_items=result2)


@bp.route('/<nickname>/add_wish', methods=['GET', 'POST'])
@login_required
def add_wish(nickname):
    """добавить желание"""
    form = AddWishForm()
    if form.validate_on_submit():
        conn = cn.get_connection()
        curs = conn.cursor()
        # заливаем желание
        sql = 'INSERT INTO item (title, about, access_level, picture) VALUES (%s, %s, %s, %s) RETURNING item_id;'
        curs.execute(sql, (form.title.data, form.about.data, form.access_level.data, form.picture.data,))
        result = curs.fetchone()
        image_path = '../static/images/wishes/wish.jpg'  # картинка по умолчанию
        # связываем желание и его степень + ползователя и предмет; указываем путь к картинке
        sql = 'INSERT INTO item_degree (item_id, degree_id) VALUES (%s, %s);' \
              'INSERT INTO user_item (id, item_id) VALUES ((SELECT id FROM users WHERE nickname = %s), %s);' \
              'UPDATE item SET picture = %s WHERE item_id = %s;'
        curs.execute(sql,
                     (result["item_id"], form.degree.data, nickname, result["item_id"], image_path, result["item_id"],))
        conn.commit()
        conn.close()
        flash('New wish was added!')
        return redirect(url_for('all_item', nickname=nickname))
    return render_template('add_wish.html', form=form)


@bp.route("/<nickname>/add_wishlist", methods=['GET', 'POST'])
@login_required
def add_wishlist(nickname):
    """создать список желаний"""
    form = AddWishListForm()
    '''желание может состоять только в одном списке, или не состоять вообще'''
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT item_id , title ' \
          'FROM (item JOIN user_item USING (item_id)) AS o ' \
          'WHERE id = %s AND giver_id IS NULL AND NOT EXISTS (SELECT * FROM item_list WHERE item_id = o.item_id);'
    curs.execute(sql, (current_user.id,))
    form.wishes.choices = [(i["item_id"], i["title"]) for i in curs.fetchall()]
    if form.validate_on_submit():
        # заливаем список
        sql = 'INSERT INTO wishlist (title, about, access_level, id) VALUES (%s, %s, %s, %s) RETURNING id;'
        curs.execute(sql, (form.title.data, form.about.data, form.access_level.data, current_user.id,))
        result = curs.fetchone()
        if len(form.wishes.data) > 0:
            # связываем список и желания в нем (если в список были добавлены желания)
            sql = 'INSERT INTO item_list(id, item_id) VALUES (%s, %s);'
            for item_id in form.wishes.data:
                curs.execute(sql, (result["id"], item_id,))
        conn.commit()
        conn.close()
        flash('New wish was added!')
        return redirect(url_for('all_item', nickname=nickname))
    conn.close()
    return render_template('add_wishlist.html', form=form)


@bp.route('/wish/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_wish(item_id):
    """изменение желания"""
    form = EditWishForm()
    if form.validate_on_submit():
        # если изменили информацию и она прошла валидацию, то данные записываются в БД
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'UPDATE item ' \
              'SET title = %s, about = %s, access_level = %s, picture = %s ' \
              'WHERE item_id = %s;' \
              'UPDATE item_degree ' \
              'SET degree_id = %s ' \
              'WHERE item_id = %s;'
        curs.execute(sql, (form.title.data, form.about.data, form.access_level.data, form.picture.data, item_id,
                           form.degree.data, item_id,))
        conn.commit()
        conn.close()
        flash('Your changes have been saved.')
        return render_template('edit_wish.html', form=form, title=form.title.data)
    elif request.method == 'GET':
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'SELECT title, about, access_level, picture, degree_id ' \
              'FROM item JOIN item_degree USING (item_id) ' \
              'WHERE item_id = %s;'
        curs.execute(sql, (item_id,))
        result = curs.fetchone()
        conn.commit()
        conn.close()
        # если метод GET, то в формы записываем данные пользователя
        form.title.data = result["title"]
        form.about.data = result["about"]
        form.access_level.data = result["access_level"]
        form.picture.data = result["picture"]
        form.degree.data = result["degree_id"]
    return render_template('edit_wish.html', form=form, title=form.title.data)


@bp.route('/list/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_wishlist(id):
    """изменение данных желания"""
    id = int(id)
    form = EditWishListForm()
    # без choices SelectMultipleField не работает // желания, которые можно добавить в список
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT item_id, title ' \
          'FROM item ' \
          'WHERE giver_id IS NULL AND item_id NOT IN (SELECT item_id FROM item_list WHERE id = %s);'
    curs.execute(sql, (id,))
    result2 = curs.fetchall()
    if len(result2) > 0:
        form.wishes.choices = result2
    if form.validate_on_submit():
        # если изменили информацию и она прошла валидацию, то данные записываются в БД
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'UPDATE wishlist ' \
              'SET title = %s, about = %s, access_level = %s ' \
              'WHERE id = %s;'
        curs.execute(sql, (form.title.data, form.about.data, form.access_level.data, id,))
        # удалим неактуальную информацию о желаниях в списке
        sql = 'DELETE FROM item_list ' \
              'WHERE id = %s'
        curs.execute(sql, (id,))
        if len(form.wishes.choices) > 0:
            # связываем список и желания в нем (если в списке есть желания)
            sql = 'INSERT INTO item_list(id, item_id) VALUES (%s, %s);'
            for item_id in form.wishes.data:
                curs.execute(sql, (id, item_id,))
        conn.commit()
        conn.close()
        flash('Your changes have been saved.')
        return render_template('edit_wishlist.html', form=form, title=form.title.data)
    elif request.method == 'GET':
        conn = cn.get_connection()
        curs = conn.cursor()
        # информация о списке
        sql = 'SELECT title, about, access_level ' \
              'FROM wishlist ' \
              'WHERE id = %s;'
        curs.execute(sql, (id,))
        result = curs.fetchone()
        conn.close()
        # если метод GET, то в формы записываем данные пользователя
        form.title.data = result["title"]
        form.about.data = result["about"]
        form.access_level.data = result["access_level"]
    return render_template('edit_wishlist.html', form=form, title=form.title.data)


@bp.route('/<item_id>/delete')
@login_required
def delete_wish(item_id):
    """удалить желание"""
    item_id = int(item_id)
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'DELETE FROM item WHERE item_id = %s AND ' \
          'item_id IN (SELECT item_id FROM user_item WHERE id = %s);'
    curs.execute(sql, (item_id, current_user.id))
    result = curs.fetchall()
    conn.close()
    return render_template('add_wish.html', wish=result)


@bp.route('/<item_id>/make_wish')
@login_required
def make_wish(item_id):
    """исполнить (зарезервировать) желание"""
    item_id = int(item_id)
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'UPDATE item ' \
          'SET giver_id = %s ' \
          'WHERE item_id = %s;'
    curs.execute(sql, (current_user.id, item_id,))
    conn.commit()
    flash('You select a wish!')
    conn.close()
    return redirect(url_for('presents'))


@bp.route('/<item_id>/fullfiled')
@login_required
def wish_fullfiled(item_id):
    """пользователь-владелец отмечает, что зарезервированное ранее желание исполнено.
    то есть зарезервированное желание удаляется"""

    '''на самом деле нужно присвоить данному предмету статус исполнено. для этого нужно проверить всю остальнюю логику 
    и отображение - слишком много времени, пока не до этого'''
    item_id = int(item_id)
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'DELETE FROM item WHERE item_id = %s;'
    curs.execute(sql, (item_id,))
    conn.commit()
    conn.close()

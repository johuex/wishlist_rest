"""модели для данных из БД"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import connectDB as cn

from app import login


class User(UserMixin):
    """Класс модели пользователя,повторяющий структуру схемы User из базы данных"""
    def __init__(self, user_id = None, phone_number = None, name = None, surname = None, userpic = None,
                 about = None, birthday = None, password_hash = None, nickname = None, email = None, last_seen = None):
        self.user_id = user_id
        self.phone_number = phone_number
        self.user_name = name
        self.surname = surname
        self.userpic = userpic
        self.about = about
        self.birthday = birthday
        self.password_hash = password_hash
        self.nickname = nickname
        self.email = email
        self.last_seen = last_seen

    def friends_wishes(self):
        """отображение последних желаний и списков друзей"""
        pass

    def set_password(self, password):
        """установка хеша пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """проверка хеша пароля"""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.user_id

    def send_request(self, user_to):
        """отправить запрос на дружбу
        на входе id пользователей"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'INSERT INTO friends_requests VALUES (%s, %s);'
        curs.execute(sql, (self.user_id, user_to,))
        conn.commit()
        conn.close()

    def accept_request(self, user_2):
        """принять запрос на дружбу"""
        conn = cn.get_connection()
        curs = conn.cursor()
        # сначала удаляем запрос на дружбу
        sql = 'DELETE FROM friends_requests WHERE (user_id_from = %s and user_id_to = %s) \
                OR (user_id_from = %s and user_id_to = %s);'
        curs.execute(sql, (self.user_id, user_2, user_2, self.user_id,))
        # затем записываем дружбу между пользователями
        sql = 'INSERT INTO friendship VALUES (%s, %s);'
        curs.execute(sql, (self.user_id, user_2,))
        conn.commit()
        conn.close()

    def reject_request(self, user_2):
        """отклонить запрос на дружбу / отменить запрос на дружбу"""
        conn = cn.get_connection()
        curs = conn.cursor()
        # удаляем запрос на дружбу
        sql = 'DELETE FROM friends_requests WHERE (user_id_from = %s and user_id_to = %s) \
                        OR (user_id_from = %s and user_id_to = %s);'
        curs.execute(sql, (self.user_id, user_2, user_2, self.user_id,))
        conn.commit()
        conn.close()

    def remove_friend(self, user_2):
        """удалить из друзей
        на входе id пользователей"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'DELETE FROM friendship WHERE (user_id_1 = %s and user_id_2 = %s) or (user_id_2 = %s and user_id_1 = %s);'
        curs.execute(sql, (self.user_id, user_2, user_2, self.user_id,))
        conn.commit()
        conn.close()

    def is_friend(self, user_2):
        """проверка на дружбу"""
        conn = cn.get_connection()
        curs = conn.cursor()
        argum = [self.user_id, user_2, user_2, self.user_id]
        sql = 'SELECT COUNT(*) FROM friendship WHERE (user_id_1 = %s and user_id_2 = %s) OR (user_id_1 = %s and user_id_2 = %s);'
        curs.execute(sql, argum)
        result = curs.fetchone()
        conn.close()
        return result[0] == 1
    # TODO почему выкидывает ошибку, если на других html

    def is_request(self, user_2):
        """проверка на запрос дружбы"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'SELECT COUNT(*) FROM friends_requests WHERE (user_id_from = %s and user_id_to = %s);'
        curs.execute(sql, (self.user_id, user_2,))
        result = curs.fetchone()
        conn.close()
        return result[0] == 1

    def friends_news(self):
        """желания и списки, добавленные недавно друзьями пользователя (не для /index)"""
        pass

    def friends_list(self):
        """показ всех друзей пользователя"""
        pass

    def requests_list(self):
        """показ всех запросов на дружбу пользователю"""
        pass
    # TODO функции показа другей и запросов на друзья
    # TODO подсчет кол-ва друзей ???

@login.user_loader
def load_user(user_id):
    """пользовательский загрузчик (связываем Flask-Login и БД)"""
    conn = cn.get_connection()
    cursor = conn.cursor()
    sql = 'SELECT * FROM users WHERE user_id = %s;'
    cursor.execute(sql, (int(user_id),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result is None:
        user = None
    else:
        user = User(result['user_id'], result['phone_number'], result['user_name'], result['surname'],
                    result['userpic'],
                    result['about'], result['birthday'], result['password_hash'], result['nickname'], result['email'],
                    result["last_seen"])
    return user


class WishList:
    """модель списка желания"""
    def __init__(self, list_id=None, user_id=None, title=None, about=None, access_level=None):
        self.list_id = list_id
        self.user_id = user_id
        self.title = title
        self.about = about
        self.access_level = access_level


class WishItem:
    """модель желания"""
    def __init__(self, item_id=None, title=None, about=None, access_level=None, picture=None, giver_id=None):
        self.item_id = item_id
        self.title = title
        self.about = about
        self.access_level = access_level
        self.picture = picture
        self.giver_id = giver_id


class GroupList:
    """модель групповых списков"""
    pass
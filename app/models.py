"""модели для данных из БД"""
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import connectDB as cn
import base64
from datetime import datetime, timedelta
import os

from app import login


class PaginatedAPIMixin(object):
    """Класс разбиения списка пользователей на страницы"""
    @staticmethod
    def to_collection_dict(required_object, condition, page, per_page, endpoint, **kwargs):
        """ создает словарь с представлением коллекции (пользователей, желаний, списков)

        :param required_object: str:требуемый объект или SQL запрос?
        :param condition: условие в WHERE
        :param page: номер страницы
        :param per_page: кол-во объектов на странице
        :param endpoint: - путь
        :param kwargs:
        :return:
        """
        # TODO как реализовать универсальное постраничное представление
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'SELECT * ' \
              'FROM %s ' \
              'WHERE id IN %s ' \
              'ORDER BY id ' \
              'OFFSET %s ROWS ' \
              'FETCH NEXT %s ROW ONLY;'
        curs.execute(sql, (required_object, condition, page*per_page, per_page))
        resources = curs.fetchall()
        # resources = query.paginate(page, per_page, False)

        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, UserMixin):
    """Класс модели пользователя,повторяющий структуру схемы User из базы данных"""
    def __init__(self, user_id=None, phone_number=None, username=None, surname=None, userpic=None,
                 about=None, birthday=None, password_hash=None, nickname=None, email=None,
                 token=None, token_expiration=None, last_seen=None):
        self.user_id = user_id
        self.phone_number = phone_number
        self.username = username
        self.surname = surname
        self.userpic = userpic
        self.about = about
        self.birthday = birthday
        self.password_hash = password_hash
        self.nickname = nickname
        self.email = email
        self.token = token
        self.token_expiration = token_expiration
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
        sql = 'INSERT INTO friend_requests VALUES (%s, %s);'
        curs.execute(sql, (self.user_id, user_to,))
        conn.commit()
        conn.close()

    def accept_request(self, user_2):
        """принять запрос на дружбу"""
        conn = cn.get_connection()
        curs = conn.cursor()
        # сначала удаляем запрос на дружбу
        sql = 'DELETE FROM friend_requests WHERE (user_id_from = %s and user_id_to = %s);'
        curs.execute(sql, (user_2, self.user_id,))
        # затем записываем дружбу между пользователями
        sql = 'INSERT INTO friendship VALUES (%s, %s), (%s, %s);'
        curs.execute(sql, (self.user_id, user_2, user_2, self.user_id,))
        conn.commit()
        conn.close()

    def reject_request(self, user_2):
        """отклонить запрос на дружбу / отменить запрос на дружбу"""
        conn = cn.get_connection()
        curs = conn.cursor()
        # удаляем запрос на дружбу
        sql = 'DELETE FROM friend_requests WHERE (user_id_from = %s and user_id_to = %s) \
                        OR (user_id_from = %s and user_id_to = %s);'
        curs.execute(sql, (self.user_id, user_2, user_2, self.user_id,))
        conn.commit()
        conn.close()

    def remove_friend(self, user_2):
        """удалить из друзей
        на входе id друга"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'DELETE FROM friendship WHERE (user_id_1 = %s and user_id_2 = %s) OR (user_id_1 = %s and user_id_2 = %s);'
        curs.execute(sql, (self.user_id, user_2, user_2, self.user_id,))
        conn.commit()
        conn.close()

    def is_friend(self, user_2):
        """проверка на дружбу"""
        conn = cn.get_connection()
        curs = conn.cursor()
        argum = [self.user_id, user_2]
        sql = 'SELECT COUNT(*) FROM friendship WHERE (user_id_1 = %s and user_id_2 = %s);'
        curs.execute(sql, argum)
        result = curs.fetchone()
        conn.close()
        return result[0] == 1

    def is_request(self, user_2):
        """проверка на запрос дружбы"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'SELECT COUNT(*) FROM friend_requests WHERE (user_id_from = %s and user_id_to = %s);'
        curs.execute(sql, (self.user_id, user_2,))
        result = curs.fetchone()
        conn.close()
        return result[0] == 1
    # TODO функции показа другей и запросов на друзья
    # TODO подсчет кол-ва друзей ???

    def to_dict(self, include_email=False):
        """перевод данных из User в dict

        :param include_email: включать ли email в ответные данные
        :return data -- : dict, который будет преобразован в JSON
        """
        data = {
            'id': self.user_id,
            'username': self.username,
            'surname': self.surname,
            'nickname': self.nickname,
            'birthday': self.birthday,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about,
            '_links': {
                'self': url_for('api.get_user', user_id=self.user_id),
                'friends': url_for('api.get_friends', user_id=self.user_id),
                # TODO добавить ссылки на желания, новости и тд
                'avatar': self.userpic
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        """ перевод данных из dict в User

        :param data: полученные данные
        :param new_user: флаг регистрации
        :return:
        """
        for field in ['username', 'nickname', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        """ возвращает токен для авторизации

        :param expires_in: время, через которое истечет время действия токена
        :return: токен
        """
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'UPDATE users ' \
              'SET token = %s ' \
              'WHERE id = %s;'
        curs.execute(sql, (self.token, self.user_id,))
        conn.commit()
        conn.close()
        return self.token

    def revoke_token(self):
        """ отзыв действующего токена

        :return:
        """
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'UPDATE users ' \
              'SET token_expiration = %s ' \
              'WHERE id = %s;'
        curs.execute(sql, (self.token_expiration, self.user_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def check_token(token):
        """ проверка жизни токена

        :param token: токен пользователя
        :return: пользователя, если токен действителен и не истек
        """
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = 'SELECT * ' \
              'FROM users ' \
              'WHERE token = %s;'
        curs.execute(sql, (token,))
        result = curs.fetchone()
        if result is None or result["token_expiration"] < datetime.utcnow():
            return None
        user = User(result['user_id'], result['phone_number'], result['username'], result['surname'],
                    result['userpic'],
                    result['about'], result['birthday'], result['password_hash'], result['nickname'],
                    result['email'], result['token'], result['token_expiration'], result["last_seen"])
        return user


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
        user = User(result['user_id'], result['phone_number'], result['username'], result['surname'],
                    result['userpic'],
                    result['about'], result['birthday'], result['password_hash'], result['nickname'], result['email'],
                    result["last_seen"])
    return user


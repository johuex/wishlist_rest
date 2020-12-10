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

    def send_request(self, user):
        """отправить запрос на дружбу"""
        pass

    def accept_request(self, user):
        """принять запрос на дружбу"""
        pass

    def reject_request(self, user):
        """отклонить запрос на дружбу"""
        pass

    def remove_friend(self, user):
        """удалить из друзей"""
        pass

    def is_friend(self, user):
        """проверка на дружбу"""
        pass


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
        list_id = list_id
        user_id = user_id
        title = title
        about = about
        access_level = access_level


class WishItem:
    """модель желания"""
    def __init__(self, item_id=None, title=None, about=None, access_level=None, picture=None, giver_id=None):
        item_id = item_id
        title = title
        about = about
        access_level = access_level
        picture = picture
        giver_id = giver_id

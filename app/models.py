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
        self.name = name
        self.surname = surname
        self.userpic = userpic
        self.about = about
        self.birthday = birthday
        self.password_hash = password_hash
        self.nickname = nickname
        self.email = email
        self.last_seen = last_seen

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.user_id


@login.user_loader
def load_user(user):
    # TODO исправить user_ID to id
    """пользовательский загрузчик (связываем Flask-Login и БД)"""
    conn = cn.get_connection()
    cursor = conn.cursor()
    sql = "SELECT 'user_ID' FROM users WHERE 'user_ID' = %s;"
    result = cursor.execute(sql, (int(user.get_id()),))
    cursor.close()
    conn.close()
    return result['user_id']


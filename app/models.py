"""модели для данных из БД"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import connectDB as cn


class User(UserMixin):
    """Класс модели пользователя,повторяющий структуру схемы User из базы данных"""
    def __init__(self, user_id = None, phone_number = None, name = None, surname = None, userpic = None,
                 about = None, birthday = None, password_hash = None, nickname = None, email = None):
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    """пользовательский загрузчик (связываем Flask-Login и БД)"""
    conn = cn.get_connection()
    cursor = conn.cursor()
    sql = "SELECT 'user_ID' FROM users WHERE 'user_ID' = %d;"
    result = cursor.execute(sql, (int(user_id),))
    cursor.close()
    conn.close()
    return result['user_id']

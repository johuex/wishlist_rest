"""модели для данных из БД"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


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




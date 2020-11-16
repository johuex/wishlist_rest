"""модели для данных из БД"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login





class User(UserMixin):
    def __init__(self, user_ID, phone_number, name, surname, userpic, about, birthday, password_hash):
        user_ID = user_ID
        phone_number = phone_number
        name = name
        surname = surname
        userpic = userpic
        about = about
        birthday = birthday
        password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
# TODO понять что это и куда пихать
'''
@login.user_loader
def load_user(user_ID):
    return User.query.get(int(user_ID))
'''
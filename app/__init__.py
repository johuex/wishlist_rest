from flask import Flask
from config import Config
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'  # перенаправим на login, если просмотр страницы требует авторизации

from app import routes

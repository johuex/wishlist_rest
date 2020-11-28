from flask import Flask
from config import Config
from flask_login import LoginManager
import connectDB as cn


app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'  # перенаправим на login, если просмотр страницы требует авторизации


@login.user_loader
def load_user(user_id):
    """пользовательский загрузчик (связываем Flask-Login и БД)"""
    conn = cn.get_connection()
    cursor = conn.cursor()
    sql = "SELECT 'user_ID' FROM users WHERE 'user_ID' = %s;"
    result = cursor.execute(sql, (int(user_id),))
    cursor.close()
    conn.close()
    return result['user_id']

from app import routes

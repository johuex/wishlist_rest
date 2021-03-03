"""
Поддержка обычной проверки подлинности данных для авторизации пользователя на API
"""
from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from app.api.errors import error_response
import connectDB as cn

basic_auth = HTTPBasicAuth()  # класс проверки подлинности email и password
token_auth = HTTPTokenAuth()  # класс проеерки подлинности токена

'''проверка подлинности email и password'''


@basic_auth.verify_password
def verify_password(email, password):
    """
    проверка пароля
    :param email: - почта пользователя
    :param password: - пароль пользователя
    :return: верность пароля
    """
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * ' \
          'FROM users ' \
          'WHERE email = %s;'
    curs.execute(sql, (email,))
    result = curs.fetchone()
    if result is None:
        return False
    user = User(result['user_id'], result['phone_number'], result['username'], result['surname'],
                result['userpic'],
                result['about'], result['birthday'], result['password_hash'], result['nickname'],
                result['email'], result['token'], result['token_expiration'], result["last_seen"])
    g.current_user = user
    return user.check_password(password)


@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)


'''проверка подлинности token пользователя'''


@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    return error_response(401)

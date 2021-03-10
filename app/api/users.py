"""API - работа с пользователями"""
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from flask import jsonify, request, url_for
from app.models import User
import connectDB as cn


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Возвращает конкретного пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * FROM users WHERE id = %s'
    curs.execute(sql, (user_id,))
    result = curs.fetchone()
    conn.close()
    if result is None:
        return bad_request("User wasn't found")
    else:
        user = User(result['id'], result['phone_number'], result['username'], result['surname'],
                    result['userpic'],
                    result['about'], result['birthday'], result['password_hash'], result['nickname'],
                    result['email'], result['token'], result['token_expiration'], result["last_seen"])
    return jsonify(user.to_dict())


@bp.route('/user/<int:user_id>/friends', methods=['GET'])
@token_auth.login_required
def get_friends(user_id):
    """Возвращает друзей конкретного пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * FROM users WHERE id = %s'
    curs.execute(sql, (user_id,))
    user = curs.fetchone()
    if user is None:
        return bad_request("User wasn't found")
    sql = 'SELECT user_id_2 ' \
          'FROM friendship ' \
          'WHERE user_id_1 = %s;'
    curs.execute(sql, (user_id,))
    result = curs.fetchall()
    friends = result["user_id_2"]
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    data = User.to_collection_dict('users', friends, page, per_page,
                                   'api.get_friends', id=id)
    conn.close()
    return jsonify(data)


@bp.route('/user', methods=['POST'])
def create_user():
    """Создание нового пользователя - полноценная регистрация"""
    data = request.get_json() or {}
    # контроль обязательных данных при полной регистрации
    if 'nickname' not in data or 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    # проверка nickname и email на повтор
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * FROM users WHERE nickname = %s'
    curs.execute(sql, (data["nickname"],))
    user = curs.fetchone()
    if user is not None:
        return bad_request('please use a different nickname')
    sql = 'SELECT * FROM users WHERE nickname = %s'
    curs.execute(sql, (data["email"],))
    user = curs.fetchone()
    if user:
        return bad_request('please use a different email address')
    # все проверки пройдены - регистрируем нового пользователя
    user = User()
    user.from_dict(data, new_user=True)
    user.set_password(data["password"])
    sql = 'INSERT INTO users (username, password_hash, nickname, email) VALUES (%s, %s, %s, %s) RETURNING id'
    curs.execute(sql, (user.username, user.password_hash, user.nickname, user.email,))
    user_id = curs.fetchone()
    conn.commit()
    conn.close()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', user_id=user_id["user_id"])
    return response


@bp.route('/user/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def update_user(user_id):
    """Изменение данных пользователя"""
    conn = cn.get_connection()
    curs = conn.cursor()
    sql = 'SELECT * FROM users WHERE id = %s'
    curs.execute(sql, (id,))
    user = curs.fetchone()
    if user is None:
        return bad_request("User wasn't found")
    data = request.get_json() or {}
    if 'username' in data and data['nickname'] != user["nickname"]:
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user["email"]:
        sql = 'SELECT * FROM users WHERE email = %s'
        curs.execute(sql, (data['email'],))
        result = curs.fetchone()
        if result is not None:
            return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    conn.commit()
    conn.close()
    return jsonify(user.to_dict())

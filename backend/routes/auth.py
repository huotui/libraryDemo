from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    
    if user.status != 'active':
        return jsonify({'code': 403, 'message': '账户已被禁用'}), 403
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': user.to_dict()
    })

@auth_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    
    user = User(
        username=data.get('username'),
        password_hash=generate_password_hash(data.get('password', '123456')),
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        role=data.get('role', 'user'),
        status=data.get('status', 'active')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 201,
        'message': '创建成功',
        'data': user.to_dict()
    })

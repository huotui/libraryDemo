from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    role = request.args.get('role', '')
    
    query = User.query
    
    if keyword:
        query = query.filter(
            db.or_(
                User.name.contains(keyword),
                User.username.contains(keyword),
                User.phone.contains(keyword)
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': user.to_dict()
    })

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    user.name = data.get('name', user.name)
    user.phone = data.get('phone', user.phone)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    user.status = data.get('status', user.status)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    })

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.username == 'admin':
        return jsonify({'code': 400, 'message': '不能删除管理员账户'}), 400
    
    from models import BorrowRecord
    borrowed = BorrowRecord.query.filter_by(user_id=user_id, status='borrowed').count()
    if borrowed > 0:
        return jsonify({'code': 400, 'message': '该用户有未归还的图书'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })

from flask import Blueprint, request, jsonify
from models import db, Category

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    
    tree = []
    for cat in categories:
        if cat.parent_id is None:
            tree.append(cat.to_dict(include_children=True))
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'tree': tree,
            'flat': [cat.to_dict() for cat in categories]
        }
    })

@categories_bp.route('', methods=['POST'])
def create_category():
    data = request.get_json()
    
    category = Category(
        name=data.get('name'),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'code': 201,
        'message': '创建成功',
        'data': category.to_dict()
    })

@categories_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    category.name = data.get('name', category.name)
    category.parent_id = data.get('parent_id', category.parent_id)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': category.to_dict()
    })

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if category.books:
        return jsonify({'code': 400, 'message': '该分类下有图书，无法删除'}), 400
    
    if category.children:
        return jsonify({'code': 400, 'message': '该分类下有子分类，无法删除'}), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })

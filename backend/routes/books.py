from flask import Blueprint, request, jsonify
from models import db, Book
from datetime import datetime

books_bp = Blueprint('books', __name__)

@books_bp.route('', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    category_id = request.args.get('category_id', type=int)
    
    query = Book.query
    
    if keyword:
        query = query.filter(
            db.or_(
                Book.title.contains(keyword),
                Book.author.contains(keyword),
                Book.isbn.contains(keyword)
            )
        )
    
    if category_id:
        query = query.filter(Book.category_id == category_id)
    
    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': [book.to_dict() for book in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': book.to_dict()
    })

@books_bp.route('', methods=['POST'])
def create_book():
    data = request.get_json()
    
    if Book.query.filter_by(isbn=data.get('isbn')).first():
        return jsonify({'code': 400, 'message': 'ISBN已存在'}), 400
    
    publish_date = None
    if data.get('publish_date'):
        try:
            publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误'}), 400
    
    total_copies = data.get('total_copies', 1)
    
    book = Book(
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        category_id=data.get('category_id'),
        publisher=data.get('publisher'),
        publish_date=publish_date,
        total_copies=total_copies,
        available_copies=total_copies
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'code': 201,
        'message': '创建成功',
        'data': book.to_dict()
    })

@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.isbn = data.get('isbn', book.isbn)
    book.category_id = data.get('category_id', book.category_id)
    book.publisher = data.get('publisher', book.publisher)
    
    if data.get('publish_date'):
        try:
            book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误'}), 400
    
    if 'total_copies' in data:
        diff = data['total_copies'] - book.total_copies
        book.total_copies = data['total_copies']
        book.available_copies = max(0, book.available_copies + diff)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': book.to_dict()
    })

@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if book.available_copies < book.total_copies:
        return jsonify({'code': 400, 'message': '该书有借阅记录，无法删除'}), 400
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })

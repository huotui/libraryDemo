from flask import Blueprint, request, jsonify, send_file, current_app
from models import db, Book
from datetime import datetime
import base64
import io
import logging
import traceback
import json

logger = logging.getLogger(__name__)

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
    try:
        data = request.get_json()
        logger.info(f'Creating book with data: {json.dumps(data, ensure_ascii=False)[:500]}...')
        
        if Book.query.filter_by(isbn=data.get('isbn')).first():
            logger.warning(f'ISBN already exists: {data.get("isbn")}')
            return jsonify({'code': 400, 'message': 'ISBN已存在'}), 400
        
        publish_date = None
        if data.get('publish_date'):
            try:
                publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
            except ValueError as e:
                logger.error(f'Invalid date format: {data.get("publish_date")}, error: {e}')
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
            available_copies=total_copies,
            image_base64=data.get('image_base64')
        )
        
        db.session.add(book)
        db.session.commit()
        
        logger.info(f'Book created successfully: id={book.id}, title={book.title}')
        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': book.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating book: {type(e).__name__}: {e}')
        logger.error(f'Request data: {json.dumps(data if "data" in locals() else {}, ensure_ascii=False)[:500]}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({'code': 500, 'message': f'创建图书失败: {str(e)}', 'detail': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        data = request.get_json()
        logger.info(f'Updating book id={book_id} with data: {json.dumps(data, ensure_ascii=False)[:500]}...')
        
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.isbn = data.get('isbn', book.isbn)
        book.category_id = data.get('category_id', book.category_id)
        book.publisher = data.get('publisher', book.publisher)
        
        if data.get('publish_date'):
            try:
                book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
            except ValueError as e:
                logger.error(f'Invalid date format: {data.get("publish_date")}, error: {e}')
                return jsonify({'code': 400, 'message': '日期格式错误'}), 400
        
        if 'total_copies' in data:
            diff = data['total_copies'] - book.total_copies
            book.total_copies = data['total_copies']
            book.available_copies = max(0, book.available_copies + diff)
        
        if 'image_base64' in data:
            image_size = len(data['image_base64']) if data['image_base64'] else 0
            logger.info(f'Updating image_base64, size: {image_size} bytes')
            book.image_base64 = data['image_base64']
        
        db.session.commit()
        
        logger.info(f'Book updated successfully: id={book_id}')
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': book.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating book id={book_id}: {type(e).__name__}: {e}')
        logger.error(f'Request data: {json.dumps(data if "data" in locals() else {}, ensure_ascii=False)[:500]}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({'code': 500, 'message': f'更新图书失败: {str(e)}', 'detail': str(e)}), 500

@books_bp.route('/<int:book_id>/image', methods=['GET'])
def download_book_image(book_id):
    book = Book.query.get_or_404(book_id)
    
    if not book.image_base64:
        return jsonify({'code': 404, 'message': '该图书暂无图片'}), 404
    
    try:
        image_data = book.image_base64
        if ',' in image_data:
            header, base64_str = image_data.split(',', 1)
        else:
            base64_str = image_data
        
        image_bytes = base64.b64decode(base64_str)
        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'book_{book_id}.jpg'
        )
    except Exception as e:
        return jsonify({'code': 500, 'message': f'图片下载失败: {str(e)}'}), 500

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

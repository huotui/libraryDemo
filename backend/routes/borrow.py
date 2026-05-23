from flask import Blueprint, request, jsonify
from models import db, Book, User, BorrowRecord
from datetime import datetime, timedelta
from config import Config

borrow_bp = Blueprint('borrow', __name__)

@borrow_bp.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    if user.status != 'active':
        return jsonify({'code': 400, 'message': '用户账户状态异常'}), 400
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'code': 404, 'message': '图书不存在'}), 404
    
    if book.available_copies <= 0:
        return jsonify({'code': 400, 'message': '该书已全部借出'}), 400
    
    borrowed_count = BorrowRecord.query.filter_by(
        user_id=user_id, 
        status='borrowed'
    ).count()
    
    if borrowed_count >= Config.MAX_BORROW_COUNT:
        return jsonify({'code': 400, 'message': f'借阅数量已达上限({Config.MAX_BORROW_COUNT}本)'}), 400
    
    existing = BorrowRecord.query.filter_by(
        user_id=user_id, 
        book_id=book_id, 
        status='borrowed'
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该书已在借阅中'}), 400
    
    borrow_record = BorrowRecord(
        user_id=user_id,
        book_id=book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=Config.BORROW_DAYS)
    )
    
    book.available_copies -= 1
    
    db.session.add(borrow_record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '借书成功',
        'data': borrow_record.to_dict()
    })

@borrow_bp.route('/return', methods=['POST'])
def return_book():
    data = request.get_json()
    record_id = data.get('record_id')
    book_id = data.get('book_id')
    
    record = None
    if record_id:
        record = BorrowRecord.query.get(record_id)
        if not record:
            return jsonify({'code': 404, 'message': '借阅记录不存在'}), 404
        if record.status != 'borrowed':
            return jsonify({'code': 400, 'message': '该记录已归还'}), 400
    elif book_id:
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'code': 404, 'message': '图书不存在'}), 404
        record = BorrowRecord.query.filter_by(
            book_id=book_id, 
            status='borrowed'
        ).first()
        if not record:
            return jsonify({'code': 400, 'message': '该书未在借阅中'}), 400
    else:
        return jsonify({'code': 400, 'message': '请提供record_id或book_id'}), 400
    
    book = Book.query.get(record.book_id)
    
    now = datetime.utcnow()
    record.return_date = now
    record.status = 'returned'
    
    fine = 0.0
    if record.due_date and now > record.due_date:
        overdue_days = (now - record.due_date).days
        fine = overdue_days * 1.0
        record.fine = fine
    
    book.available_copies += 1
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '还书成功',
        'data': record.to_dict()
    })

@borrow_bp.route('/records', methods=['GET'])
def get_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    user_id = request.args.get('user_id', type=int)
    
    query = BorrowRecord.query
    
    if keyword:
        query = query.join(User).join(Book).filter(
            db.or_(
                User.name.contains(keyword),
                Book.title.contains(keyword)
            )
        )
    
    if status:
        query = query.filter(BorrowRecord.status == status)
    
    if user_id:
        query = query.filter(BorrowRecord.user_id == user_id)
    
    pagination = query.order_by(BorrowRecord.borrow_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })

@borrow_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    today = datetime.utcnow().date()
    
    today_borrows = BorrowRecord.query.filter(
        db.func.date(BorrowRecord.borrow_date) == today
    ).count()
    
    current_borrows = BorrowRecord.query.filter_by(status='borrowed').count()
    
    overdue_records = BorrowRecord.query.filter(
        BorrowRecord.status == 'borrowed',
        BorrowRecord.due_date < datetime.utcnow()
    ).count()
    
    recent_records = BorrowRecord.query.order_by(
        BorrowRecord.borrow_date.desc()
    ).limit(10).all()
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'today_borrows': today_borrows,
            'current_borrows': current_borrows,
            'overdue_count': overdue_records,
            'recent_records': [r.to_dict() for r in recent_records]
        }
    })

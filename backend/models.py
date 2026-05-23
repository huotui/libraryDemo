from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'))
    
    books = db.relationship('Book', backref='category', lazy=True)
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id
        }
        if include_children and self.children:
            data['children'] = [child.to_dict(include_children=True) for child in self.children]
        return data

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    publisher = db.Column(db.String(100))
    publish_date = db.Column(db.Date)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)
    
    def to_dict(self):
        category_name = self.category.name if self.category else '未分类'
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category_id': self.category_id,
            'category_name': category_name,
            'publisher': self.publisher,
            'publish_date': self.publish_date.strftime('%Y-%m-%d') if self.publish_date else None,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')
    fine = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        user_name = self.user.name if self.user else '未知'
        book_title = self.book.title if self.book else '未知'
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': user_name,
            'book_id': self.book_id,
            'book_title': book_title,
            'borrow_date': self.borrow_date.strftime('%Y-%m-%d %H:%M:%S') if self.borrow_date else None,
            'return_date': self.return_date.strftime('%Y-%m-%d %H:%M:%S') if self.return_date else None,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else None,
            'status': self.status,
            'fine': self.fine
        }

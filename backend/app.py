from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.books import books_bp
from routes.borrow import borrow_bp
from routes.users import users_bp
from routes.categories import categories_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    CORS(app)
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(borrow_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    
    with app.app_context():
        db.create_all()
        migrate_database()
        init_data()
    
    return app

def migrate_database():
    """Database migration for adding new columns"""
    import sqlite3
    import os
    
    db_path = os.path.join(os.path.dirname(__file__), 'library.db')
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'image_base64' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN image_base64 TEXT")
            conn.commit()
            print("Database migration completed: Added image_base64 column to books table")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

def init_data():
    from models import User, Category, Book
    from werkzeug.security import generate_password_hash
    
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin'),
            name='系统管理员',
            role='admin'
        )
        db.session.add(admin)
    
    if not User.query.filter_by(username='test').first():
        test_user = User(
            username='test',
            password_hash=generate_password_hash('test'),
            name='测试用户',
            role='user'
        )
        db.session.add(test_user)
        
    if Category.query.count() == 0:
        categories = ['文学', '历史', '科学', '技术', '教育', '艺术', '经济', '哲学']
        for cat_name in categories:
            category = Category(name=cat_name)
            db.session.add(category)
    
    if Book.query.count() == 0:
        books_data = [
            ('活着', '余华', '9787506365437', 1, '作家出版社'),
            ('百年孤独', '加西亚·马尔克斯', '9787544253994', 1, '南海出版公司'),
            ('人类简史', '尤瓦尔·赫拉利', '9787508647357', 2, '中信出版社'),
            ('Python编程从入门到实践', 'Eric Matthes', '9787115428028', 4, '人民邮电出版社'),
            ('时间简史', '史蒂芬·霍金', '9787535732309', 3, '湖南科学技术出版社'),
            ('艺术的故事', '贡布里希', '9787807463726', 6, '广西美术出版社'),
        ]
        for title, author, isbn, cat_id, publisher in books_data:
            book = Book(
                title=title,
                author=author,
                isbn=isbn,
                category_id=cat_id,
                publisher=publisher,
                total_copies=999,
                available_copies=999
            )
            db.session.add(book)
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8888)

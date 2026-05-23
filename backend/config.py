import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'library.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'library-secret-key-2024'
    BORROW_DAYS = 30
    MAX_BORROW_COUNT = 5

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'key123')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///seloedu.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024 
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    THUMBMAIL_SIZE = (200,200)
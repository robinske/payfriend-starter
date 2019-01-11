import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    AUTHY_API_KEY = os.environ.get('AUTHY_API_KEY')
    db_path = os.path.join(os.path.dirname(__file__), 'payfriend.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

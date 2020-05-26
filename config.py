import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

#SECRET_KEY = os.environ.get('SECRET_KEY')
#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
#SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config:
    #SECRET_KEY = b'\xb5\xf52e\xc7`nXo\xfd\xed\x1f\x99@T\xf0'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/refresh'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_CSRF_COOKIE_PATH = '/'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    SECRET_KEY = "dev"
    JWT_SECRET = "jwt-dev"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    #SECRET_KEY = b'\xb5\xf52e\xc7`nXo\xfd\xed\x1f\x99@T\xf0'
    SECRET_KEY = "test"
    JWT_SECRET = "jwt-test"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductinConfig(Config):
    #SECRET_KEY = b'\xb5\xf52e\xc7`nXo\xfd\xed\x1f\x99@T\xf0'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductinConfig,
    'default': DevelopmentConfig
}

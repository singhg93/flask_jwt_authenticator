import os
import datetime
import click

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import config

def create_app(config_name='default'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY ="dev",
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'database.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        JWT_SECRET = "dev",
        JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1),
        JWT_TOKEN_LOCATION = ['cookies'],
        JWT_ACCESS_COOKIE_PATH = '/auth',
        JWT_REFRESH_COOKIE_PATH = '/auth/refresh',
        JWT_COOKIE_CSRF_PROTECT = True,
        JWT_COOKIE_SECURE = False
    )

    #load the instance config if it exists when not testing
    #app.config.from_pyfile('config.py', silent=True)

    #app.config.from_mapping(
    #    SECRET_KEY ="dev",
    #    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'database.sqlite'),
    #    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    #    JWT_SECRET = "dev",
    #    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    #)

    #load the instance config if it exists when not testing
    #app.config.from_pyfile('config.py', silent=True)
    app.config.from_object(config[config_name])

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .models import db, User, bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    # initialize the migration command
    migrate = Migrate(app, db)

    # pass the app context to the views
    #with app.app_context():
    # import the registration and authentication api from views
    from .views.auth_api import(
        jwt, RegisterAPI, AuthenticateAPI, RefreshAPI, FreshLogin, ValidateToken, ValidateFreshToken, Home, LogoutAPI
    )
    jwt.init_app(app)
    # add the url rules
    app.add_url_rule('/auth/register', view_func=RegisterAPI.as_view('register'))
    app.add_url_rule('/auth/login', view_func=AuthenticateAPI.as_view('login'))
    app.add_url_rule('/auth/logout', view_func=LogoutAPI.as_view('logout'))
    app.add_url_rule('/auth/refresh', view_func=RefreshAPI.as_view('refresh'))
    app.add_url_rule('/auth/fresh_login', view_func=FreshLogin.as_view('fresh_login'))
    app.add_url_rule('/auth/validate_token', view_func=ValidateToken.as_view('validate_token'))
    app.add_url_rule('/auth/validate_fresh_token', view_func=ValidateFreshToken.as_view('validate_fresh_token'))
    app.add_url_rule('/auth/home', view_func=Home.as_view('home'))

    # register the test module to add the "flask test" click command
    import tests
    tests.test_init_app(app)

    return app


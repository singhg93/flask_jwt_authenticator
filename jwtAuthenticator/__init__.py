import os
import datetime

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY ="dev",
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'database.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        JWT_SECRET = "dev",
        JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    )

    if test_config is None:
        #load the instance config if it exists when not testing
        #app.config.from_pyfile('config.py', silent=True)
        app.config.from_object(Config)
    else:
        # load the config that is passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .models import db, User
    db.init_app(app)

    # initialize the migration command
    migrate = Migrate(app, db)

    # pass the app context to the views
    with app.app_context():
        # import the registration and authentication api from views
        from .views.auth_api import(
            RegisterAPI, AuthenticateAPI, RefreshAPI, FreshLogin, ValidateToken, ValidateFreshToken, Home
        )
        # add the url rules
        app.add_url_rule('/auth/register', view_func=RegisterAPI.as_view('register'))
        app.add_url_rule('/auth/login', view_func=AuthenticateAPI.as_view('login'))
        app.add_url_rule('/auth/refresh', view_func=RefreshAPI.as_view('refresh'))
        app.add_url_rule('/auth/fresh_login', view_func=FreshLogin.as_view('fresh_login'))
        app.add_url_rule('/auth/validate_token', view_func=ValidateToken.as_view('validate_token'))
        app.add_url_rule('/auth/validate_fresh_token', view_func=ValidateFreshToken.as_view('validate_fresh_token'))
        app.add_url_rule('/auth/home', view_func=Home.as_view('home'))

    return app

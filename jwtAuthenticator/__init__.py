import os

from flask import Flask
from .models import db, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI= 'sqlite:///' + os.path.join(app.instance_path, 'database.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
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

    migrate = Migrate(app, db)

    @app.route('/hello')
    def hello_world():
        return "Hello, World"

    #from .views import auth_api 
    #app.register_blueprint(auth_api.api_bp)

    # pass the app context to the views
    with app.app_context():
        # import the registration and authentication api from views
        from .views.auth_api import RegisterAPI, AuthenticateAPI
        # add the url rules
        app.add_url_rule('/api/register', view_func=RegisterAPI.as_view('register'))
        app.add_url_rule('/api/authenticate', view_func=AuthenticateAPI.as_view('authenticate'))

    return app

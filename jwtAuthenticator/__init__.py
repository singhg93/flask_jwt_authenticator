import os

from flask import Flask
from .models import db, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
#from config import Config

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI= 'sqlite:///' + os.path.join(app.instance_path, 'database.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    # initialize bcrypt
    bcrypt = Bcrypt(app)

    if test_config is None:
        #load the instance config if it exists when not testing
        app.config.from_pyfile('config.py', silent=True)
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

    return app

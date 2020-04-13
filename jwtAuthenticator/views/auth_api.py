import functools
import json
from flask_bcrypt import Bcrypt
from jwtAuthenticator.schemas.schema_user import validate_user
from jwtAuthenticator import db
from jwtAuthenticator.models import User

from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity
)

from flask import (
    Blueprint, request, jsonify
)

bcrypt = Bcrypt()

api_bp = Blueprint('api', __name__, url_prefix='/api')

#@api_bp.route("/test", methods=['GET'])
#def test_route():
#    passwordHash = bcrypt.generate_password_hash("hello")
#    return passwordHash

@api_bp.route('/register', methods=['POST'])
def register():
    ''' user registration endpoint '''
    data = validate_user(request.get_json())

    # if the validation succeeded
    if data['ok']:
        # get the user data
        user_data = data['user_data']
        # create the hash of the password
        user_data['password'] = bcrypt.generate_password_hash(user_data['password'])
        # create a new user and save it in the database
        newUser = User(username=user_data['username'], password=user_data['password'])
        db.session.add(newUser)
        db.session.commit()
        # send the reponse with a message indicating a successful registration
        return jsonify({'ok': True, 'message': 'User Created'}), 200

    # validation did not succeed
    else:
        # send the response with a message indicating a bad request
        return jsonify({'ok': False, 'message': 'Bad Request Parameters'}), 400


@api_bp.route('/authenticate', methods=['POST'])
def authenticate():
    ''' user authentication endpoint '''

    # validate the request data
    data = validate_user(request.get_json())

    # if validataion was successful
    if data['ok']:
        user_data = data['user_data']
        user = User.query.get(username=user_data['username'])
        if user and bcrypt.check_password_hash(user_data['password']):
            pass

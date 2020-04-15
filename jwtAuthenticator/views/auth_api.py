import functools
import json
from jwtAuthenticator.schemas.schema_user import validate_user
from jwtAuthenticator import db
from jwtAuthenticator.models import User
from flask.views import MethodView
from flask import current_app
from flask_bcrypt import Bcrypt

from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity
)

from flask import (
    Blueprint, request, jsonify
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
bcrypt = Bcrypt(current_app)
jwt = JWTManager(current_app)

#@api_bp.route("/test", methods=['GET'])
#def test_route():
#    passwordHash = bcrypt.generate_password_hash("hello")
#    return passwordHash

#@api_bp.route('/register', methods=['POST'])
class RegisterAPI(MethodView):

    def get(self):
        return jsonify({'ok': False, 'message': 'forbidden'}), 403

    def post(self):
        ''' user registration endpoint '''
        data = validate_user(request.get_json())

        # if the validation succeeded
        if data['ok']:
            # get the user data
            user_data = data['user_data']
            # create the hash of the password
            user_data['password'] = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
            # create a new user and save it in the database
            newUser = User(username=user_data['username'], password=user_data['password'])

            # if the User with the given username already exists
            if (User.query.filter_by(username=user_data['username']).first()):
                # send the username already exists in the json response
                return jsonify({'ok': False, 'message': 'Username already exists'}), 400

            # add the user in the database
            db.session.add(newUser)
            db.session.commit()
            # send the reponse with a message indicating a successful registration
            return jsonify({'ok': True, 'message': 'User Created'}), 200

        # validation did not succeed
        else:
            # send the response with a message indicating a bad request
            print(data['message'])
            return jsonify({'ok': False, 'message': 'Bad Request Parameters'}), 400


#@api_bp.route('/authenticate', methods=['POST'])
class AuthenticateAPI(MethodView):

    def get(self):
        return jsonify({'ok': False, 'message': 'forbidden'}), 403

    def post(self):
        ''' user authentication endpoint '''

        # validate the request data
        data = validate_user(request.get_json())

        # if validataion was successful
        if data['ok']:

            # get the user data from the validated data
            user_data = data['user_data']

            # get teh user from the data from database if it exists
            user = User.query.filter_by(username=user_data['username']).first()

            # if the user with the given username exists and the password is valid
            print(user.password)
            print(user_data['password'])
            if user and bcrypt.check_password_hash(user.password, user_data['password']):

                # remove the password from the userdata
                del user_data['password']
                # create the access token
                access_token = create_access_token(identity=user_data)
                refresh_token = create_refresh_token(identity=user_data)
                user_data['access_token'] = access_token
                user_data['refresh_token'] = refresh_token
                return jsonify({'ok': True, 'data': user_data}), 200

            else:
                # the user does not exist or the password is not valid, return invalid credentials
                return jsonify({'ok': False, 'message': 'Invalid Credentials'}), 400

import functools
import json
from jwtAuthenticator.schemas.schema_user import validate_user
from jwtAuthenticator.models import db
from jwtAuthenticator.models import User
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from flask import current_app

from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, fresh_jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_csrf_token
)

from flask import (
    request, jsonify
)

bcrypt = Bcrypt()
jwt = JWTManager()


# registration endpoint
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

            if data['error'] == 'validation':
                return jsonify({'ok': False, 'message': 'Bad input values'}), 400

            # send the response with a message indicating a bad request
            return jsonify({'ok': False, 'message': 'Bad Request Parameters'}), 400


# authentication endpoint
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
            if user and bcrypt.check_password_hash(user.password, user_data['password']):

                # remove the password from the userdata
                del user_data['password']
                # create the access token
                access_token = create_access_token(identity=user_data, fresh=True)
                refresh_token = create_refresh_token(identity=user_data)
                #user_data['access_token'] = access_token
                #user_data['refresh_token'] = refresh_token
                user_data['login'] = True
                resp = jsonify(user_data)
                set_access_cookies(resp, access_token)
                set_refresh_cookies(resp, refresh_token)
                return resp, 200

            else:
                # the user does not exist or the password is not valid, return invalid credentials
                return jsonify({'ok': False, 'message': 'Invalid Credentials'}), 400
        else:

            if data['error'] == 'validation':
                return jsonify({'ok': False, 'message': 'Invalid Credentials'}), 400

            # the user does not exist or the password is not valid, return invalid credentials
            return jsonify({'ok': False, 'message': 'Bad Request'}), 400


# recreate accessToken
class RefreshAPI(MethodView):
    ''' view for refreshing jwt tokens '''

    # get not allowed
    def get(self):
        return jsonify({'ok': False, 'message': 'forbidden'}), 403

    # the refresh token is required to access this url
    @jwt_refresh_token_required
    def post(self):
        ''' access token refresh endpoint '''
        # get the current user
        current_user = get_jwt_identity()
        # create a new token
        access_token = create_access_token(identity=current_user, fresh=False)

        # response
        resp = jsonify({'refresh': True})
        set_access_cookies(resp, access_token)

        # return the access_token in refresh token
        return resp, 200

# fresh login
class FreshLogin(MethodView):
    ''' view to create fresh access tokens '''
    
    def get(self):
        return jsonify({'ok': False, 'message': 'forbidden'}), 403

    @jwt_required
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
            if user and bcrypt.check_password_hash(user.password, user_data['password']):

                # remove the password from the userdata
                del user_data['password']

                #user_data['access_token'] = access_token
                user_data['fresh_login'] = True

                # create the access token
                access_token = create_access_token(identity=user_data, fresh=True)

                # create a response
                resp = jsonify(user_data)
                set_access_cookies(resp, access_token)

                return resp, 200

            else:
                # the user does not exist or the password is not valid, return invalid credentials
                return jsonify({'ok': False, 'message': 'Invalid Credentials'}), 400


class ValidateToken(MethodView):
    ''' token validation endpoint '''

    # validate the token
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        return jsonify({"ok": True, 'is_valid': True, 'user': current_user}), 200

    # not implemented
    @jwt_required
    def post(self):
        #current_user = get_jwt_identity()
        #return jsonify({"ok": True, 'message': 'The token is valid', 'user': current_user}), 200
        current_user = get_jwt_identity()
        return jsonify({"ok": True, 'is_valid': True, 'user': current_user}), 200

class ValidateFreshToken(MethodView):
    ''' fresh token validation '''

    # validate the token and verify it is fresh
    @fresh_jwt_required
    def get(self):
        current_user = get_jwt_identity()
        return jsonify({"ok": True, 'is_valid': True, 'user': current_user}), 200

    @fresh_jwt_required
    def post(self):
        current_user = get_jwt_identity()
        return jsonify({"ok": True, 'is_valid': True, 'user': current_user}), 200


class LogoutAPI(MethodView):
    ''' logout token validation '''

    # remove the tokens from cookies
    def get(self):
        return jsonify({'ok': False, 'message': 'forbidden'}), 403

    def post(self):
        resp = jsonify({'logout': True})
        # remove the cookies from the response
        unset_jwt_cookies(resp)
        return resp, 200


#TODO: This is just a test
class Home(MethodView):
    ''' This is just to test frontend '''

    def get(self):
        return "This is a home in get"

    def post(self):
        return "this is a home in post"

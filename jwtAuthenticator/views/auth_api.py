import functools
import json
from jwtAuthenticator.schemas.schema_user import validate_user
from jwtAuthenticator.models import db
from jwtAuthenticator.models import User
from flask.views import MethodView

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    fresh_jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)

from flask import (
    request, jsonify
)

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

            # create a new user and save it in the database
            newUser = User(username=user_data['username'], password=user_data['password'])

            # if the User with the given username already exists
            if (User.query.filter_by(username=user_data['username']).first()):
                # send the username already exists in the json response
                return jsonify({'ok': False, 'message': 'duplicate_username'}), 400

            # add the user in the database
            db.session.add(newUser)
            db.session.commit()
            # send the reponse with a message indicating a successful registration
            return jsonify({'ok': True, 'message': 'User Created'}), 200

        # validation did not succeed
        else:

            if data['error'] == 'validation':
                #message = ""
                #if data['message'] == 'username':
                #    message = "Username must be at least 4 characters "
                #    message += "and can only contain _ @ ! and no spaces"
                #elif data['message'] == 'password':
                #    message = "Password must be atleast 8 characters in length "
                #    message += "and must contain a capital letter, a small letter, "
                #    message += "a number and a special character"
                return jsonify({'ok': False, 'message': "Invalid Credentials"}), 400

            # send the response with a message indicating a bad request
            return jsonify({'ok': False, 'message': "Bad Credentials"}), 400


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
            if user and user.verify_password(user_data['password']):

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
            if user and user.verify_password(user_data['password']):

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

class GetUsers(MethodView):
    
    def get(self):
        all_users = User.query.order_by(User.username).all()
        #return jsonify({'ok': True, 'data': all_users}), 200
        json_encodeable_users = [a_user.as_dict() for a_user in all_users]
        return jsonify({'ok': True, 'data': json_encodeable_users}, 200)

#TODO: This is just a test
class Home(MethodView):
    ''' This is just to test frontend '''

    def get(self):
        resp = jsonify({'message': "this is home in get"})
        return resp, 200

    def post(self):
        resp = jsonify({'message': "this is home in post"})
        return resp, 200

import unittest
from http.cookiejar import CookieJar
from jwtAuthenticator import create_app
from jwtAuthenticator.models import db, User
import json

class AuthClientTestCase(unittest.TestCase):

    def setUp(self):
        '''
        Run this before running any test
        Create an app with testing config
        Get the app context
        Create all the tables
        '''
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        '''
        After the tests are done
        remove the database session
        drop all the tables
        remove the app context
        '''
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home(self):
        '''
        Test the home url 
        '''
        response = self.client.get('/auth/home')
        # The response status code should be 200, i.e. the request was successful
        self.assertEqual(response.status_code, 200)
        # The response should contain the following text
        self.assertTrue('This is a home' in response.get_data(as_text=True))

    def test_user_registration(self):
        '''
        Test user registration endpoint
        '''
        # register a new user
        response = self.client.post('/auth/register',
            # set the content type header to json
            content_type = 'application/json',
            # send the data for creating a new user
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # the user should be successfully created and the response status
        # code should be positive i.e. 200
        self.assertEqual(response.status_code, 200)

    def test_user_registration_fail(self):
        '''
        Test bad user registration
        '''

        # register a new user with invalid password specification
        response = self.client.post('/auth/register',
            # set the content type header to json
            content_type = 'application/json',
            # give the data to be sent with the request
            data = json.dumps({
                'username': 'test',
                # the password is not valid because it does not meet specifications
                'password': 'password3@'
            }))
        # the request should not be successfull, i.e. the request code should be 400
        self.assertEqual(response.status_code, 400)

    def test_empty_username_registration_fail(self):
        '''
        Test bad username registration
        '''
        # register a new user with incorrect username specification
        response = self.client.post('/auth/register',
            # set the content type header
            content_type = 'application/json',
            # set the data to be sent with the request
            data = json.dumps({
                # username is incorrect as it can't be empty, so the request
                # should not be successful
                'username': '',
                'password': 'password3@'
            }))
        # the request should not be successful, i.e. the response status code should be 400
        self.assertEqual(response.status_code, 400)

    def test_empty_password_registration_fail(self):
        '''
        Test no password given registration
        '''
        # register a new user with incorrect password specification
        response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                # password given is invalid, so request should not be successful
                'password': ''
            }))
        # The request should not be successful, i.e. the response status code should be 400
        self.assertEqual(response.status_code, 400)

    def test_user_registration_authentication(self):
        '''
        Test user login
        '''
        # register a new user and test if he is authenticated
        response_register = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user is successfully created
        self.assertEqual(response_register.status_code, 200)

        # send the request to login endpoint with user credentials
        response_login = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # Test user is logged in properly, i.e. request was successful
        self.assertEqual(response_login.status_code, 200)

    def test_user_registration_bad_authentication(self):
        '''
        Test bad credentials login attempt
        '''
        # register a new user and test if he is authenticated
        response_register = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test user is created
        self.assertEqual(response_register.status_code, 200)

        # test user login endpoint with bad user credentials
        response_login = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                # the password is incorrect
                'password': 'password123@'
            }))
        # The login attmpt should fail and response status code should be 400
        self.assertEqual(response_login.status_code, 400)

    def test_bad_username_authentication(self):
        '''
        Test wrong username correct password login attmpt
        '''
        # register a new user and test if he is authenticated
        response_register = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that a user is created successfully
        self.assertEqual(response_register.status_code, 200)

        # test the login endpoint with wrong username
        response_login = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'wrongUsername',
                'password': 'Password123@'
            }))
        # The login attempt should fail and response status code should be 400
        self.assertEqual(response_login.status_code, 400)

    def test_refresh_login(self):
        '''
        Test refresh access_token endpoint
        '''
        # create a new user
        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # assert that the user is created successfully
        self.assertEqual(register_response.status_code, 200)
        # Login the user and save the response to a variable
        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # check that the user is created successfully
        self.assertEqual(login_response.status_code, 200)
        # get the refresh token from the response cookies
        refresh_token_cookie = self.get_access_token_cookie(login_response, "refresh_token_cookie")
        # get the csrf token from the cookies
        csrf_refresh_token = self.get_access_token_cookie(login_response, "csrf_refresh_token")
        # test the refresh endpoint using refresh_token cookies and csrf_token cookies
        refresh_response = self.client.post('/auth/refresh',
            content_type = 'application/json',
            headers = {
                'Set-Cookie': refresh_token_cookie,
                'X-CSRF-TOKEN': csrf_refresh_token.split('=')[1].split(';')[0]
                },
            )
        # test that the response status code is successfull
        self.assertEqual(refresh_response.status_code, 200)

    def test_fresh_login(self):
        '''
        Test fresh access_token login
        '''
        # register the user
        register_response = self.client.post('/auth/register', 
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user is created successfully
        self.assertEqual(register_response.status_code, 200)
        # login the user using the fresh login endpoint
        login_response = self.client.post('/auth/fresh_login', 
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user successfully logged in
        self.assertEqual(login_response.status_code, 200)

    def test_validate_token(self):
        '''
        Test token validation endpoint
        '''

        # register the user
        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user is created successfully
        self.assertEqual(register_response.status_code, 200)

        # log the user in
        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user was successfully logged in
        self.assertEqual(login_response.status_code, 200)
        # get csrf token and access token from the cookies
        csrf_access_token = self.get_access_token_cookie(login_response, "csrf_access_token")
        access_token_cookie = self.get_access_token_cookie(login_response, "access_token_cookie")

        # send a request to token validation endpoint with access token and csrf token
        refresh_response = self.client.post('/auth/validate_token',
            content_type = 'application/json',
            headers = {
                'Set-Cookie': access_token_cookie,
                'X-CSRF-TOKEN': csrf_access_token.split('=')[1].split(';')[0]
                },
            )
        # assert that the resonse was successful
        self.assertEqual(refresh_response.status_code, 200)

    def test_validate_fresh_token(self):
        '''
        Test validate fresh token endpoint
        '''
        # register a new user
        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the registration was successful
        self.assertEqual(register_response.status_code, 200)

        # log the user in
        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user was logged in
        self.assertEqual(login_response.status_code, 200)
        # get the access token and csrf token from the cookies
        csrf_access_token = self.get_access_token_cookie(login_response, "csrf_access_token")
        access_token_cookie = self.get_access_token_cookie(login_response, "access_token_cookie")
        # get the resonse from the fresh token validation endpoint
        fresh_validation_response = self.client.post('/auth/validate_fresh_token',
            content_type = 'application/json',
            headers = {
                'Set-Cookie': access_token_cookie,
                'X-CSRF-TOKEN': csrf_access_token.split('=')[1].split(';')[0]
                },
            )
        # check that the token was validated
        self.assertEqual(fresh_validation_response.status_code, 200)

    def test_logout(self):
        '''
        Logout endpoin test
        '''
        # register a new user
        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user was registered
        self.assertEqual(register_response.status_code, 200)

        # log the user in
        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        # test that the user was logged in
        self.assertEqual(login_response.status_code, 200)
        # get the csrf token and access token
        csrf_access_token = self.get_access_token_cookie(login_response, "csrf_access_token")
        access_token_cookie = self.get_access_token_cookie(login_response, "access_token_cookie")
        # send a request to logout endpoint
        logout_response = self.client.post('/auth/logout')
        # test that the request was successful
        self.assertEqual(logout_response.status_code, 200)

    # funcion to get the cookies from a response object
    def get_access_token_cookie(self, response, cookie_name):
        # get the headers from the response object
        cookies = response.headers
        # for each tuple in the headers
        for a_cookie in cookies:
            # get the first element as the key and the second element as cookie value
            key, value = a_cookie
            # if the value starts with the required cookie name then return the value
            if value.startswith(cookie_name):
                return value

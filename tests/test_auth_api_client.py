import unittest
from http.cookiejar import CookieJar
from jwtAuthenticator import create_app
from jwtAuthenticator.models import db, User
import json

class AuthClientTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home(self):
        response = self.client.get('/auth/home')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('This is a home' in response.get_data(as_text=True))

    def test_user_registration(self):

        # register a new user
        response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(response.status_code, 200)

    def test_user_registration_fail(self):

        # register a new user with incorrect password specification
        response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'password3@'
            }))
        self.assertEqual(response.status_code, 400)

    def test_empty_username_registration_fail(self):

        # register a new user with incorrect password specification
        response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': '',
                'password': 'password3@'
            }))
        self.assertEqual(response.status_code, 400)

    def test_empty_password_registration_fail(self):

        # register a new user with incorrect password specification
        response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': ''
            }))
        self.assertEqual(response.status_code, 400)

    def test_user_registration_authentication(self):

        # register a new user and test if he is authenticated
        response_register = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(response_register.status_code, 200)

        response_login = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(response_login.status_code, 200)

    def test_user_registration_bad_authentication(self):

        # register a new user and test if he is authenticated
        response_register = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(response_register.status_code, 200)

        response_login = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'password123@'
            }))
        self.assertEqual(response_login.status_code, 400)

    def test_user_registration_bad_authentication(self):

        # register a new user and test if he is authenticated
        response_register = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'wrongUsername',
                'password': 'Password123@'
            }))
        self.assertEqual(response_register.status_code, 200)

        response_login = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'password123@'
            }))
        self.assertEqual(response_login.status_code, 400)

    def test_refresh_login(self):

        # test refresh token

        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))

        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(login_response.status_code, 200)
        refresh_token_cookie = self.get_access_token_cookie(login_response, "refresh_token_cookie")
        csrf_refresh_token = self.get_access_token_cookie(login_response, "csrf_refresh_token")

        refresh_response = self.client.post('/auth/refresh',
            content_type = 'application/json',
            headers = {
                'Set-Cookie': refresh_token_cookie,
                'X-CSRF-TOKEN': csrf_refresh_token.split('=')[1].split(';')[0]
                },
            )

        self.assertEqual(refresh_response.status_code, 200)

    def test_fresh_login(self):
        register_response = self.client.post('/auth/register', 
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(register_response.status_code, 200)
        login_response = self.client.post('/auth/fresh_login', 
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(login_response.status_code, 200)

    def test_validate_token(self):
        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))

        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(login_response.status_code, 200)
        csrf_access_token = self.get_access_token_cookie(login_response, "csrf_access_token")
        access_token_cookie = self.get_access_token_cookie(login_response, "access_token_cookie")

        refresh_response = self.client.post('/auth/validate_token',
            content_type = 'application/json',
            headers = {
                'Set-Cookie': access_token_cookie,
                'X-CSRF-TOKEN': csrf_access_token.split('=')[1].split(';')[0]
                },
            )

        self.assertEqual(refresh_response.status_code, 200)

    def test_validate_fresh_token(self):
        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))

        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(login_response.status_code, 200)
        csrf_access_token = self.get_access_token_cookie(login_response, "csrf_access_token")
        access_token_cookie = self.get_access_token_cookie(login_response, "access_token_cookie")

        refresh_response = self.client.post('/auth/validate_fresh_token',
            content_type = 'application/json',
            headers = {
                'Set-Cookie': access_token_cookie,
                'X-CSRF-TOKEN': csrf_access_token.split('=')[1].split(';')[0]
                },
            )

        self.assertEqual(refresh_response.status_code, 200)

    def test_logout(self):
        register_response = self.client.post('/auth/register',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))

        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post('/auth/login',
            content_type = 'application/json',
            data = json.dumps({
                'username': 'test',
                'password': 'Password123@'
            }))
        self.assertEqual(login_response.status_code, 200)
        csrf_access_token = self.get_access_token_cookie(login_response, "csrf_access_token")
        access_token_cookie = self.get_access_token_cookie(login_response, "access_token_cookie")

        logout_response = self.client.post('/auth/logout')
        self.assertEqual(logout_response.status_code, 200)

    def get_access_token_cookie(self, response, cookie_name):
        cookies = response.headers
        for a_cookie in cookies:
            key, value = a_cookie
            if value.startswith(cookie_name):
                return value

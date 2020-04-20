import unittest
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

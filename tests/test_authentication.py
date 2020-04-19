import unittest
from flask import current_app
from jwtAuthenticator import create_app
from jwtAuthenticator.models import User, db
from jwtAuthenticator.views.auth_api import jwt

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)


    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

class BasicHomeTest(unittest.TestCase):
    def get_api_headers(self):
        return {
            'Content-Type': 'application/json'
        }




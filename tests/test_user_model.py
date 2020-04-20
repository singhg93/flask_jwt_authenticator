import unittest
from jwtAuthenticator.models import User

class UserModelTestCase(unittest.TestCase):

    def test_password_setter(self):
        user = User(username="test", password="human")
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User(username="test", password="human")
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(password="human")
        self.assertTrue(user.verify_password("human"))
        self.assertFalse(user.verify_password("robot"))

    def test_password_salts_are_random(self):
        user1 = User(password="robot")
        user2 = User(password="robot")
        self.assertTrue(user1.password_hash != user2.password_hash)

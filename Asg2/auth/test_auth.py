from pydoc import resolve
import unittest
from app import app
import json
import utils

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True


    def test_validate_none_token(self):
        response = self.app.get('/users/validate', headers={'Authorization': None})
        self.assertEqual(json.loads(response.data)['code'], 403)
        self.assertEqual(json.loads(response.data)['message'], "forbidden: jwt is invalid")


    def test_validate_none_user(self):
        response = self.app.get('/users/validate', headers={'Authorization': 'a doesnt exist token'})
        self.assertEqual(json.loads(response.data)['code'], 403)
        self.assertEqual(json.loads(response.data)['message'], "forbidden: jwt is invalid")


    def test_validate_valid(self):
        response = self.app.get('/users/validate', headers={'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODI0NDc2OTAsInVzZXJuYW1lIjoieHloIn0.nQx0yFyV_uIjuiVcdYCvZZWa6NRbPnLS4HlvTD4Tchc'})
        self.assertEqual(json.loads(response.data)['code'], 200)


    def test_user_login_none_username_or_password(self):
        response = self.app.post('/users/login', data=json.dumps({'username': None, 'password': None}), content_type='application/json')
        self.assertEqual(json.loads(response.data)['code'], 403)


    def test_users_post_none_username_or_password(self):
        response = self.app.post('/users', data=json.dumps({'username': None, 'password': None}), content_type='application/json')
        self.assertEqual(json.loads(response.data)['code'], 400)


    def test_users_post_none_user(self):
        response = self.app.post('/users', data=json.dumps({'username': 'xyh', 'password': 'xyh'}), content_type='application/json')
        self.assertEqual(json.loads(response.data)['code'], 409)
    

    def test_users_put_none_username_or_password(self):
        response = self.app.put('/users', data=json.dumps({'username': 'xyh', 'old-password': 'xyh', 'new-password': 'xyh'}), content_type='application/json')
        self.assertEqual(json.loads(response.data)['code'], 200)


    def test_users_put_none_user(self):
        response = self.app.put('/users', data=json.dumps({'username': 'no this user', 'old-password': 'xyh', 'new-password': 'xyh'}), content_type='application/json')
        self.assertEqual(json.loads(response.data)['code'], 403)


    def test_users_put_none_user(self):
        response = self.app.put('/users', data=json.dumps({'username': 'no this user', 'old-password': 'xyh', 'new-password': 'xyh'}), content_type='application/json')
        self.assertEqual(json.loads(response.data)['code'], 403)


if __name__ == '__main__':
    unittest.main()
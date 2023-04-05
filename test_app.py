import unittest
from app import app
import json

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_root(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        self.assertEqual(json.loads(response.data)['code'], 200)

    def test_post_root(self):
        response = self.app.post('/', data=json.dumps({'url': 'http://www.google.com'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        self.assertEqual(json.loads(response.data)['code'], 201)

if __name__ == '__main__':
    unittest.main()
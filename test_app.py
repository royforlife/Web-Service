from pydoc import resolve
import unittest
from app import app
import json

test_valid_url = 'http://www.google.com'
test_invalid_url = 'http://www.googl.com1'
test_invalid_id = 'aninvalidid'
test_invalid_user = 'invaliduser'

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_root(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        self.assertEqual(json.loads(response.data)['code'], 200)

    def test_delete_root(self):
        response = self.app.delete('/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 404)

    def test_post_valid_root(self):
        for i in range(100000):
            test_url = 'http://www.google.com/' + str(i)
            response = self.app.post('/', data=json.dumps({'url': test_url}), content_type='application/json')
            self.assertEqual(response.status_code, 201)
            self.assertEqual(json.loads(response.data)['status'], 'success')
            self.assertEqual(json.loads(response.data)['code'], 201)

    def test_post_invalid_root(self):
        response = self.app.post('/', data=json.dumps({'url': test_invalid_url}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)['data']['message'], 'invalid url')
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 400)

    def test_get_root_invalid_id(self):
        response = self.app.get('/'+test_invalid_id)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 404)

    def test_get_root_valid_id(self):
        returned = self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json')
        valid_id = json.loads(returned.data)['data']['id']
        response = self.app.get('/'+valid_id)
        self.assertEqual(response.status_code, 302)

    def test_put_root_valid_id_valid_auth(self):
        returned = self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json')
        valid_id = json.loads(returned.data)['data']['id']
        response = self.app.put('/'+valid_id, headers={'Authorization': 'default'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        self.assertEqual(json.loads(response.data)['code'], 200)

    def test_put_root_valid_id_valid_auth(self):
        returned = self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json')
        valid_id = json.loads(returned.data)['data']['id']
        response = self.app.put('/'+valid_id, headers={'Authorization': test_invalid_user})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)['data']['message'], 'Authorization Forbidden')
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 400)
    
    def test_put_root_invalid_id(self):
        response = self.app.put('/'+test_invalid_id)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 404)

    def test_delete_root_invalid_id(self):
        response = self.app.delete('/'+test_invalid_id, headers={'Authorization': 'user123'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 404)

    def test_delete_root_valid_id_invalid_user(self):
        returned = self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json')
        valid_id = json.loads(returned.data)['data']['id']
        response = self.app.delete('/'+valid_id, headers={'Authorization': test_invalid_user})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.data)['data']['message'], 'Authorization Forbidden')
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 403)

    def test_delete_root_valid_id_valid_user(self):
        # get a 'Authorization': 'default'
        self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json')
        returned = self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json')
        valid_id = json.loads(returned.data)['data']['id']
        response = self.app.delete('/'+valid_id, headers={'Authorization': 'default'})
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()
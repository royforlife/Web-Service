from pydoc import resolve
import unittest
from app import app
import json

test_valid_url = 'http://www.google.com'
test_invalid_url = 'http://www.googl.com1'
# This must be invalid because it doesn't fit the syntax of hashids, includs i and l
test_invalid_id = 'aninvalidid'
test_valid_id1 = 'c'
test_valid_id2 = 'i'
test_invalid_user = 'invaliduser'

correct_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODI0NDc2OTAsInVzZXJuYW1lIjoieHloIn0.nQx0yFyV_uIjuiVcdYCvZZWa6NRbPnLS4HlvTD4Tchc"

wrong_token = "1234567"

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_correct_token_root(self):
        """ Test response of getting all the data from the database with correct token
        Request: GET
        """
        response = self.app.get('/', headers={'Authorization': correct_token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        self.assertEqual(json.loads(response.data)['code'], 200)

    def test_get_wrong_token_root(self):
        """ Test response of getting all the data from the database with wrong token
        Request: GET
        """
        response = self.app.get('/', headers={'Authorization': wrong_token})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 403)

    def test_post_valid_url_correct_token_root(self):
        """ Test posting an invalid URL with correct token
        Request: POST
        """
        response = self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json', headers={'Authorization': correct_token})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        self.assertEqual(json.loads(response.data)['code'], 201)

    def test_post_invalid_url_correct_token_root(self):
        """ Test posting an invalid URL with correct token
        Request: POST
        """
        response = self.app.post('/', data=json.dumps({'url': test_invalid_url}), content_type='application/json', headers={'Authorization': correct_token})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 400)

    def test_post_valid_url_wrong_token_root(self):
        """ Test posting an invalid URL with wrong token
        Request: POST
        """
        response = self.app.post('/', data=json.dumps({'url': test_valid_url}), content_type='application/json', headers={'Authorization': wrong_token})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 403)

    def test_post_invalid_url_wrong_token_root(self):
        """ Test posting an invalid URL with wrong token
        Request: POST
        """
        response = self.app.post('/', data=json.dumps({'url': test_invalid_url}), content_type='application/json', headers={'Authorization': wrong_token})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 403)

    def test_delete_correct_token_root(self):
        """ Test response of deleting data from the database with correct token.
        Request: DELETE
        """
        response = self.app.delete('/', headers={'Authorization': correct_token})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 404)

    def test_delete_wrong_token_root(self):
        """ Test response of deleting data from the database with wrong token.
        Request: DELETE
        """
        response = self.app.delete('/', headers={'Authorization': wrong_token})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 403)

    def test_put_id_correct_token_root(self):
        """ Test update data from the database with correct token.
        Request: PUT
        """
        response = self.app.put('/'+test_valid_id1, data=json.dumps({'url': test_valid_url}), content_type='application/json', headers={'Authorization': correct_token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        self.assertEqual(json.loads(response.data)['code'], 200)

    def test_put_id_wrong_token_root(self):
        """ Test update data from the database with wrong token.
        Request: PUT
        """
        response = self.app.put('/'+test_valid_id1, data=json.dumps({'url': test_valid_url}), content_type='application/json', headers={'Authorization': wrong_token})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.data)['status'], 'error')
        self.assertEqual(json.loads(response.data)['code'], 403)

    def test_delete_id_wrong_token_root(self):
        """ Test response of deleting data from the database with wrong token.
        Request: DELETE
        """
        response = self.app.put('/'+test_valid_id2, headers={'Authorization': wrong_token})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.data)['data']['message'], 'forbidden')
        self.assertEqual(json.loads(response.data)['code'], 403)



if __name__ == '__main__':
    unittest.main()
import time
import hashlib
import jwt
import string
import random

APP_SECRET = 'web-service-auth'
JWT_SECRET = 'this_is_a_jwt_secret'


def create_credentials(username, password):
    # create a random salt
    try:
        val = password + APP_SECRET + username
        _md5 = hashlib.md5()
        _md5.update(val.encode('utf-8'))
        return _md5.hexdigest()
    except:
        return None


def generate_token(username):
    payload = {
        'username': username,
        'start': int(time.time()),
        'expire': int(time.time()) + 60*60*24*7
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        if payload['expire'] < time.time():
            return None
    except:
        return None
    return payload['username']

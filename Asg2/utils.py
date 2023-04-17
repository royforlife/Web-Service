import time
import hashlib
from JWT import JWT
import string
import random

APP_SECRET = 'web-service-auth'
JWT_SECRET = 'this_is_a_jwt_secret'
EXPIRE_TIME = 60*60


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
    }
    return JWT.encode(payload, JWT_SECRET, EXPIRE_TIME)


def decode_token(token):
    if token is None:
        return None
    try:
        payload = JWT.decode(token, JWT_SECRET)
        if payload is None or 'username' not in payload.keys():
            return None
        return payload['username']
    except:
        return None


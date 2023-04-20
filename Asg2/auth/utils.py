import time
import hashlib
from JWT import JWT
import string
import random
import os

APP_SECRET = 'web-service-auth'
JWT_SECRET = 'this_is_a_jwt_secret'
EXPIRE_TIME = 60*60*24*7

# read APP_SECRET and JWT_SECRET from environment variables
# APP_SECRET = os.environ.get('APP_SECRET')
# JWT_SECRET = os.environ.get('JWT_SECRET')
# EXPIRE_TIME = os.environ.get('EXPIRE_TIME')


def create_credentials(username, password):
    # create credentials for the user which is a hash of username and password
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
    # generate JWT token
    return JWT.encode(payload, JWT_SECRET, EXPIRE_TIME)


def decode_token(token):
    # decode the token, get the user if token is valid, else return None
    if token is None:
        return None
    try:
        # decode the token
        payload = JWT.decode(token, JWT_SECRET)
        if payload is None or 'username' not in payload.keys():
            return None
        # return the username
        return payload['username']
    except:
        return None


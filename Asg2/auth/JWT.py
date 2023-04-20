import base64
import json
import time
import hmac
import hashlib

# code reference source: https://blog.csdn.net/key_world/article/details/109634148
class JWT():
    @staticmethod
    def encode(payload_origin, secret, exp=3600):
        header = {
            'typ': 'JWT',
            'alg': 'HS256'
        }
        # serialize header
        header_json = json.dumps(header, separators=(',', ':'), sort_keys=True)
        # encode header
        header_json_base64 = JWT.b64encode(header_json.encode('utf-8'))
        payload = payload_origin.copy()
        # add exp which is the current time plus exp to payload
        payload['exp'] = int(time.time()) + exp
        # serialize and encode payload
        payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        payload_json_base64 = JWT.b64encode(payload_json.encode('utf-8'))
        # sign with secret, header and payload
        sign = hmac.new(secret.encode('utf-8'), header_json_base64 + b'.' + payload_json_base64, digestmod="SHA256")
        # encode sign
        sign_base64 = JWT.b64encode(sign.digest())

        return header_json_base64 + b'.' + payload_json_base64 + b'.' + sign_base64

    @staticmethod
    def b64encode(data):
        # use urlsafe_b64encode to replace b64encode to make sure the token is url safe
        return base64.urlsafe_b64encode(data).replace(b'=', b'')

    @staticmethod
    def b64decode(data):
        # use urlsafe_b64decode to replace b64decode to make sure the token is url safe
        return base64.urlsafe_b64decode(data + b'=' * (4 - len(data) % 4))

    @staticmethod
    def decode(token, secret):
        try:
            # split token
            header_json_base64, payload_json_base64, sign_base64 = token.encode().split(b'.')
            # re-create sign with secret, header and payload
            sign = hmac.new(secret.encode('utf-8'), header_json_base64 + b'.' + payload_json_base64, digestmod="SHA256")
            # verify sign
            if sign_base64 != JWT.b64encode(sign.digest()):
                return None

            # decode payload
            payload_json = JWT.b64decode(payload_json_base64)
            # deserialize payload
            payload = json.loads(payload_json)
            # compare the exp with current time to verify exp
            if int(payload['exp']) < int(time.time()):
                return None
            return payload
        except:
            return None
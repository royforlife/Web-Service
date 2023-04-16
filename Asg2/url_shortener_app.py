import os, re
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import urllib.request
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import utils

# Create a Flask app instance
app = Flask(__name__)
# Initialize the database
POSTGRES_URI = 'postgresql://postgres:postgres@localhost:5432/data'
engine = create_engine(POSTGRES_URI)
if not database_exists(engine.url):
    create_database(engine.url)

app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI

# Integrates SQLAlchemy with Flask
db = SQLAlchemy(app)
# Initialize the Hashids object to encode URLs


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin_url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)

    def __init__(self, origin_url, short_url, user):
        self.origin_url = origin_url
        self.short_url = short_url
        self.user = user


with app.app_context():
    db.create_all()

def validate_url(url: str):
    """Determinate the validity of a URL.
    1 Checking syntax 2. Checking if it is available on the Internet

    Args:
        URL (String): A URL with indeterminate validity

    Returns:
        Boolean: the validity of the URL
        :param url:
    """
    if url is None:
        return False
    if not re.match(r'^https?:/{2}\w.+$', url):
        return False
    try:
        urllib.request.urlopen(url)
    except Exception as e:
        return False
    return True

# create a function that maps number to a short String with the alphabet(a-z, A-Z, 0-9)
def create_ID(num):
    # Map to store 62 possible characters
    map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    shorturl = ""
    # Convert given integer id to a base 62 number
    while (num):
        shorturl += map[num % 62]
        num = num // 62
    # Reverse shortURL to complete base conversion
    shorturl = shorturl[::-1]
    return shorturl

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def route_root():
    """
    A Flask route that handles GET, POST, and DELETE requests for a URL shortener service.
    """
    # GET method: returns a JSON object containing all shortened URLs in the database.
    user = request.headers.get('Authorization')
    user = utils.decode_token(user)
    # Assign each URL an authorization
    if user == '' or user is None:
        return jsonify({'status': 'error', 'data': {'message': 'forbidden'}, 'code': 403}), 403
    else:
        if request.method == 'GET':
            all_urls = Url.query.all()
            return jsonify({'status': 'success', 'data': {'urls': [url.short_url for url in all_urls]}, 'code': 200}), 200

        # POST method: if the URL is valid, it is added to the database with a new unique short URL.
        # If the URL is invalid, an error response is returned.
        elif request.method == 'POST':
            if 'url' in request.json.keys() and validate_url(request.json['url']):
                origin_url = request.json['url']
                user = request.headers.get('Authorization')
                user = utils.decode_token(user)
                # Assign each URL an authorization
                if user == '' or user is None:
                    return jsonify({'status': 'error', 'data': {'message': 'token invalid or expired'}, 'code': 400}), 400
                short_url = origin_url
                new_url = Url(origin_url, short_url, user=user)
                db.session.add(new_url)
                db.session.commit()
                # Encode the id of the new URL with Hashids to generate a short URL
                db.session.query(Url).filter_by(id=new_url.id).update({'short_url': create_ID(new_url.id)})
                db.session.commit()
                return jsonify({'status': 'success', 'data': {'id': new_url.short_url}, 'code': 201}), 201
            else:
                return jsonify({'status': 'error', 'data': {'message': 'invalid url or url not exist'}, 'code': 400}), 400

        # DELETE method: returns a 404 error as the root cannot be deleted.
        elif request.method == 'DELETE':
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404


@app.route('/<key>', methods=['GET', 'PUT', 'DELETE'])
def route_id(key):
    """
    This function maps HTTP requests for the shortened URL key to appropriate response message.

    Args:
        key (str): The shortened URL key(id).
    """
    # GET requests: retrieves the original URL from the database and redirects to it.
    user = request.headers.get('Authorization')
    user = utils.decode_token(user)
    if request.method == 'GET':
        urls = Url.query.filter_by(short_url=key).all()
        if len(urls) == 0:
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404
        else:
            # redirect to origin_url if it is valid
            if validate_url(urls[0].origin_url):
                return redirect(urls[0].origin_url)
            else:
                return jsonify({'status': 'success', 'data': {'url': urls[0].origin_url}, 'code': 301}), 301

    # PUT requests: updates the original URL for the provided shortened URL key.
    elif request.method == 'PUT':
        if user == '' or user is None:
            return jsonify({'status': 'error', 'data': {'message': 'forbidden'}, 'code': 403}), 403
        else:
            new_url = request.json['url']

            if new_url is None or not validate_url(new_url):
                return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 400}), 400
            urls = Url.query.filter_by(short_url=key).all()
            if len(urls) > 0:
                # Users only have operational access to their own URLs
                user = request.headers.get('Authorization')
                user = utils.decode_token(user)
                # Assign each URL an authorization
                if user == '' or user is None:
                    return jsonify({'status': 'error', 'data': {'message': 'token invalid or expired'}, 'code': 400}), 400
                urls = Url.query.filter_by(short_url=key, user=user).all()
                if len(urls) > 0:
                    db.session.query(Url).filter_by(id=urls[0].id).update({'origin_url': new_url})
                    db.session.commit()
                    return jsonify({'status': 'success'}), 200
                else:
                    return jsonify({'status': 'error', 'data': {'message': 'Authorization Forbidden'}, 'code': 403}), 403

            else:
                return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404

    # DELETE requests: deletes the original URL from the database.
    elif request.method == 'DELETE':
        if user == '' or user is None:
            return jsonify({'status': 'error', 'data': {'message': 'forbidden'}, 'code': 403}), 403
        else:
            urls = Url.query.filter_by(short_url=key).all()

            if len(urls) == 0:
                return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404
            else:
                # Users only have deleted access to their own URLs
                urls = Url.query.filter_by(short_url=key, user=user).all()
                if len(urls) == 0:
                    return jsonify({'status': 'error', 'data': {'message': 'Authorization Forbidden'}, 'code': 403}), 403
                else:
                    db.session.delete(urls[0])
                    db.session.commit()
                    return jsonify({'status': 'success', 'data': {'message': 'delete success'}, 'code': 204}), 204


if __name__ == '__main__':
    app.run()

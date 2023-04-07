import os, re
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from hashids import Hashids
import urllib.request

# Create Flask app instance
app = Flask(__name__)
# Initialize database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# Integrates SQLAlchemy with Flask
db = SQLAlchemy(app)
# Initialize Hashids object to encode URLs
hashids = Hashids(min_length=2)


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin_url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)

    def __init__(self, origin_url, short_url, user):
        self.origin_url = origin_url
        self.short_url = short_url
        self.user = user


def validate_url(url: str) -> bool:
    """Determinates the validity of a url. 
    1 Checing syntax 2. Checking if it is available on the Internet

    Args:
        url (String): A url with indeterminate validity

    Returns:
        Boolean: the validity of the url
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


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def route_root():
    """
    A Flask route that handles GET, POST, and DELETE requests for a URL shortener service.

    Returns:
        _type_: The HTTP response to the request.
    """
    # GET method: returns a JSON object containing all shortened URLs in the database.
    if request.method == 'GET':
        all_urls = Url.query.all()
        return jsonify({'status': 'success', 'data': {'urls': [url.short_url for url in all_urls]}, 'code': 200}), 200

    # POST method: if the URL is valid, it is added to the database with a new unique short URL. If the URL is invalid, an error response is returned.
    elif request.method == 'POST':
        if 'url' in request.json.keys() and validate_url(request.json['url']):
            origin_url = request.json['url']
            user = request.headers.get('Authorization')
            # Assign each url an authorization
            if user == '' or user is None:
                user = 'default'
            short_url = origin_url
            new_url = Url(origin_url, short_url, user=user)
            db.session.add(new_url)
            db.session.commit()
            db.session.query(Url).filter_by(id=new_url.id).update({'short_url': hashids.encode(new_url.id)})
            db.session.commit()
            return jsonify({'status': 'success', 'data': {'id': new_url.short_url}, 'code': 201}), 201
        else:
            return jsonify({'status': 'error', 'data': {'message': 'invalid url or url not exist'}, 'code': 400}), 400
    
    # DELETE method: returns a 404 error as the root endpoint cannot be deleted.
    elif request.method == 'DELETE':
        return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404


@app.route('/<key>', methods=['GET', 'PUT', 'DELETE'])
def route_id(key):
    
    """
    This function maps HTTP requests for the shortened URL key to appropriate response.

    Args:
        key (str): The shortened URL key(id).

    Returns:
        Response: The HTTP response to the request.
    """

    # GET requests: retrieves the original URL from the database and redirects to it.
    if request.method == 'GET':
        urls = Url.query.filter_by(short_url=key).all()
        if len(urls) == 0:
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404
        else:
            # Redict to origin_url if it is valid
            if validate_url(urls[0].origin_url):
                return redirect(urls[0].origin_url)
            else:
                return jsonify({'status': 'success', 'data': {'url': urls[0].origin_url}, 'code': 301}), 301

    # PUT requests: updates the original URL for the provided shortened URL key.
    elif request.method == 'PUT':
        
        new_url = request.json['url']
        
        if new_url is None or not validate_url(new_url):
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 400}), 400
        urls = Url.query.filter_by(short_url=key).all()
        if len(urls) > 0:
            # Each user only have operational access to their url
            user = request.headers.get('Authorization')
            if user == '' or user is None:
                user = 'default'
            urls = Url.query.filter_by(short_url=key, user=user).all()
            if len(urls) > 0:
                db.session.query(Url).filter_by(id=urls[0].id).update({'origin_url': new_url})
                db.session.commit()
                return jsonify({'status': 'success', 'data': {}}), 200
            else:
                return jsonify({'status': 'error', 'data': {'message': 'Authorization Forbidden'}, 'code': 403}), 403
        
        else:
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404
    
    # DELETE requests: deletes the original URL from the database for the provided shortened URL key.
    elif request.method == 'DELETE':
        
        urls = Url.query.filter_by(short_url=key).all()

        if len(urls) == 0:
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404}), 404
        else:
            # Users only hava delete access to their url
            user = request.headers.get('Authorization')
            if user == '' or user is None:
                user = 'default'
            urls = Url.query.filter_by(short_url=key, user=user).all()
            if len(urls) == 0:
                return jsonify({'status': 'error', 'data': {'message': 'Authorization Forbidden'}, 'code': 403}), 403
            else:
                db.session.delete(urls[0])
                db.session.commit()
                return jsonify({'status': 'success', 'data': {'message': 'delete success'}, 'code': 204}), 204


if __name__ == '__main__':
    app.run()

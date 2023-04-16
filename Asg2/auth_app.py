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
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.Text, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


with app.app_context():
    db.create_all()

@app.route('/users', methods=['POST', 'PUT'])
def route_register():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        if username is None or password is None:
            return jsonify({'status': 'error', 'message': 'username or password is missing', 'code': 400}), 400
        if User.query.filter_by(username=username).first() is not None:
            return jsonify({'status': 'error', 'message': 'duplicate', 'code': 409}), 409
        password = utils.create_credentials(username, password)
        if password is None:
            return jsonify({'status': 'error', 'message': 'password not valid', 'code': 400}), 400
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'user created successfully', 'code': 201}), 201
    elif request.method == 'PUT':
        username = request.json['username']
        old_password = request.json['old-password']
        new_password = request.json['new-password']
        if username is None or old_password is None or new_password is None:
            return jsonify({'status': 'error', 'message': 'Forbidden: username or password is missing', 'code': 403}), 403
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({'status': 'error', 'message': 'Forbidden: username does not exist', 'code': 403}), 403
        current_credentials = utils.create_credentials(username, old_password)
        if current_credentials is None or current_credentials != user.password:
            return jsonify({'status': 'error', 'message': 'forbidden', 'code': 403}), 403
        new_credentials = utils.create_credentials(username, new_password)
        if new_credentials is None:
            return jsonify({'status': 'error', 'message': 'forbidden', 'code': 403}), 403
        user.password = new_credentials
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'password changed successfully', 'code': 200}), 200


@app.route('/users/login', methods=['POST'])
def route_login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        if username is None or password is None:
            return jsonify({'status': 'error', 'message': 'forbidden: username or password is missing', 'code': 403}), 403
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({'status': 'error', 'message': 'forbidden: username does not exist', 'code': 403}), 403
        current_credentials = utils.create_credentials(username, password)
        if current_credentials is None or current_credentials != user.password:
            return jsonify({'status': 'error', 'message': 'forbidden', 'code': 403}), 403
        token = utils.generate_token(username)
        return jsonify({'status': 'success', 'message': 'login successful', 'code': 200, 'jwt': token}), 200


if __name__ == '__main__':
    app.run()
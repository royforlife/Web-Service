import os, requests, json, re
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from hashids import Hashids
import urllib.request
from datetime import datetime, timedelta
from sqlalchemy import event
from flask_apscheduler import APScheduler


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
db = SQLAlchemy(app)
hashids = Hashids()


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin_url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, origin_url, short_url, user):
        self.origin_url = origin_url
        self.short_url = short_url
        self.user = user


# everytime the outdated data is expired, it will response for the last time and will be delated
@event.listens_for(Url, 'load') # wired, but some other options(expect for load) doesn't work
def check_url_age(target, context): # context is useless but needed
    current_time = datetime.utcnow()
    created_date = target.created_date
    
    # calculate the time difference, set to expire after a certain time(like 10 hour)
    if current_time - created_date > timedelta(seconds=60):
        db.session.delete(target)
        db.session.commit()
    '''
    or we consider: return jsonify({'status': 'error', 'data': {'message': 'expired'}, 'code': 404})
    or update the created_date of target object in the database, i.e. refresh
    '''
    # else:
    #    
    #     target.created_date = current_time
    #     db.session.flush()
    #     db.session.commit()


def validate_url(url):
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
    if request.method == 'GET':
        all_urls = Url.query.all()
        return jsonify({'status': 'success', 'data': {'urls': [url.short_url for url in all_urls]}, 'code': 200})

    elif request.method == 'POST':
        # todo add user
        if 'url' in request.json.keys() and validate_url(request.json['url']):
            origin_url = request.json['url']
            user = request.headers.get('Authorization')
            if user == '' or user is None:
                user = 'default'
            short_url = origin_url
            new_url = Url(origin_url, short_url, user=user)
            db.session.add(new_url)
            db.session.commit()
            db.session.query(Url).filter_by(id=new_url.id).update({'short_url': hashids.encode(new_url.id)})
            db.session.commit()
            return jsonify({'status': 'success', 'data': {'id': new_url.short_url}, 'code': 201})
        else:
            return jsonify({'status': 'error', 'data': {'message': 'invalid url'}, 'code': 400})
    elif request.method == 'DELETE':
        return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404})


@app.route('/<key>', methods=['GET', 'PUT', 'DELETE'])
def route_id(key):
    if request.method == 'GET':
        urls = Url.query.filter_by(short_url=key).all()
        if len(urls) == 0:
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404})
        else:
            # redict to origin_url if it is valid
            if validate_url(urls[0].origin_url):
                return redirect(urls[0].origin_url)
            else:
                return jsonify({'status': 'success', 'data': {'url': urls[0].origin_url}, 'code': 301})

    elif request.method == 'PUT':
        urls = Url.query.filter_by(short_url=key).all()
        if len(urls) > 0:
            user = request.headers.get('Authorization')
            if user == '' or user is None:
                user = 'default'

            urls = Url.query.filter_by(short_url=key, user=user).all()
            # todo: return 200, only relative user can update
            if len(urls) > 0:
                original_url = urls[0].origin_url
                # delete old url
                db.session.delete(urls[0])
                db.session.commit()
                # add new url
                short_url = original_url
                new_url = Url(original_url, short_url, user=user)
                db.session.add(new_url)
                db.session.commit()
                db.session.query(Url).filter_by(id=new_url.id).update({'short_url': hashids.encode(new_url.id)})
                db.session.commit()
                return jsonify({'status': 'success', 'data': {'id': new_url.short_url}, 'code': 201})
            else:
                # todo: retuen 403 Forbidden
                return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 403})

        else:
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404})
    elif request.method == 'DELETE':
        urls = Url.query.filter_by(short_url=key).all()
        if len(urls) == 0:
            return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 404})
        else:
            # todo: only relative user can delete
            user = request.headers.get('Authorization')
            if user == '' or user is None:
                user = 'default'
            urls = Url.query.filter_by(short_url=key, user=user).all()
            if len(urls) == 0:
                # todo: retuen 403 Forbidden
                return jsonify({'status': 'error', 'data': {'message': 'error'}, 'code': 403})
            else:
                db.session.delete(urls[0])
                db.session.commit()
                return jsonify({'status': 'success', 'data': {'message': 'success'}, 'code': 204})

'''
Timed task for clearing out-of-date data
Beware: app.app_context()
'''
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
# misfire_grace_time: specifies the number of seconds that the scheduler will wait for the task to execute before marking it as "misfired". 
@scheduler.task('interval', id='do_job_1', seconds=10, misfire_grace_time=900)
def update_db():
    current_time = datetime.utcnow()
    # to deal with RuntimeError: Working outside of application context
    with app.app_context():
        outdated_urls = Url.query.filter(Url.created_date < (current_time - timedelta(seconds=60))).all()
        for url in outdated_urls:
            db.session.delete(url)
            db.session.commit()


if __name__ == '__main__':
    app.run()

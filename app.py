#-*-coding:utf-8-*-

import json
import redis
from functools import wraps
from flask import Flask, request, session, redirect, render_template, Response
from config import APP_KEY, APP_SECRET, REDIRECT_URL, ALBUM_NAME
from renren import APIClient, APIError
import background as backend

kv = redis.Redis()
renren = APIClient(APP_KEY, APP_SECRET, REDIRECT_URL, version=1)

app = Flask(__name__)
app.secret_key = 'j1e'


# jsonify response decorator
def jsonify(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return Response(json.dumps(f(*args, **kwargs)), mimetype='application/json')
    return wrapped


def auth_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not 'uid' in session:
            return {'status': 'error', 'msg': 'no permission'}, 403
        else:
            return f(*args, **kwargs)
    return wrapped


@app.route('/')
def index():

    def redirect_to_auth_url():
        scopes = ['read_user_photo', 'read_user_album', 'send_notification',
                  'send_request', 'publish_feed', 'status_update', 'photo_upload',
                  'create_album', 'operate_like']
        return render_template('login.html', login_url=renren.get_authorize_url(scope=scopes, redirect_uri=REDIRECT_URL))

    if 'uid' not in session:
        return redirect_to_auth_url()

    uid = session['uid']

    access_token, uname, avatar, target = kv.hmget('user:%d' % uid, ['access_token', 'uname', 'avatar', 'target'])
    renren.set_access_token(access_token)

    try:
        visit_count = renren.users.getProfileInfo(uid=uid, fields='visitors_count').get('visitors_count')
    except APIError, e:
        session.pop('uid', None)
        return redirect_to_auth_url()

    return render_template('index.html', uname=uname.decode('utf-8'),
                           avatar=avatar, target=int(target) if target else 0, visit_count=visit_count)


@app.route('/callback')
def auth_callback():
    code = request.args.get('code')
    if not code:
        return 'error'

    result = renren.request_access_token(code)
    user = result.pop('user')
    session['uid'] = uid = user['id']

    result.update({
        'uid': uid,
        'uname': user['name'].encode('utf-8'),
        'avatar': user['avatar'][0]['url']
    })
    result.pop('token_type')
    result.pop('scope')

    kv.hmset('user:%d' % uid, result)

    return redirect('/')


@app.route('/get_target')
@jsonify
@auth_required
def get_target():
    uid = session['uid']
    target = kv.hget('user:%d' % uid, 'target')

    return {'target': int(target) if target else 0}


@app.route('/set_target', methods=['POST'])
@jsonify
@auth_required
def set_target():
    uid = session['uid']
    new_target = request.form.get('value')

    old_target, access_token = kv.hmget('user:%d' % uid, ['target', 'access_token'])
    running, _, _ = backend.background_query_job(uid)
    if not running:
        backend.background_add_job(uid, access_token, new_target)
    else:
        backend.background_update_job_target(uid, new_target)

    kv.hset('user:%d' % uid, 'target', new_target)

    return {
        'status': 'ok',
        'first_time': False if old_target else True
    }


@app.route('/pause', methods=['POST'])
@jsonify
@auth_required
def pause_job():
    uid = session['uid']
    backend.background_del_job(uid)
    return {
        'status': 'ok'
    }


@app.route('/resume', methods=['POST'])
@jsonify
@auth_required
def resume_job():
    uid = session['uid']
    target, access_token = kv.hmget('user:%d' % uid, ['target', 'access_token'])
    backend.background_add_job(uid, access_token, target)
    return {
        'status': 'ok'
    }


@app.route('/status')
@jsonify
@auth_required
def get_status():
    uid = session['uid']
    running, now_visit_count, timestamp = backend.background_query_job(uid)
    return {
        'running': running
    }

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

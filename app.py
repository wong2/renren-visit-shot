#-*-coding:utf-8-*-

import json
import redis
from flask import Flask, request, session, redirect, render_template, Response
from config import APP_KEY, APP_SECRET, REDIRECT_URL
from renren import APIClient

kv = redis.Redis()
renren = APIClient(APP_KEY, APP_SECRET, REDIRECT_URL, version=1)

app = Flask(__name__)
app.secret_key = 'j1e'

# jsonify response decorator
def jsonify(f):
    def wrapped(*args, **kwargs):
        return Response(json.dumps(f(*args, **kwargs)), mimetype='application/json')
    return wrapped

@app.route('/')
def index():
    if 'uid' not in session:
        return render_template('login.html', login_url=renren.get_authorize_url())

    uid = session['uid']

    access_token, uname, avatar, target = kv.hmget('user:%d' % uid, ['access_token', 'uname', 'avatar', 'target'])
    renren.set_access_token(access_token)

    visit_count = renren.users.getProfileInfo(uid=uid, fields='visitors_count').get('visitors_count')

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

    kv.hmset('user:%d' % uid, result)

    return redirect('/')

@app.route('/get_target')
def get_target():
    if not 'uid' in session:
        return 'no permission', 403

    uid = session['uid']
    target = kv.hget('user:%d' % uid, 'target')

    return target if target else '0'

@app.route('/set_target', methods=['POST'])
@jsonify
def set_target():
    if not 'uid' in session:
        return 'no permission', 403

    uid = session['uid']
    target = request.form.get('value')

    kv.hset('user:%d' % uid, 'target', target)

    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True)

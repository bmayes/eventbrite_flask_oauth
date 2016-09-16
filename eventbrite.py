from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

eventbrite = oauth.remote_app(
    'eventbrite',
    consumer_key='[your key]',
    consumer_secret='[your secret]',
    base_url='https://www.eventbriteapi.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.eventbrite.com/oauth/token',
    authorize_url='https://www.eventbrite.com/oauth/authorize'
)


@app.route('/')
def index():
    if 'eventbrite_token' in session:
        me = eventbrite.get('user')
        return jsonify(me.data)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return eventbrite.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('eventbrite_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():

    resp = eventbrite.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['eventbrite_token'] = (resp['access_token'], '')
    me = eventbrite.get('/v3/users/me/')
    return jsonify(me.data)


@eventbrite.tokengetter
def get_eventbrite_oauth_token():
    return session.get('eventbrite_token')


if __name__ == '__main__':
    app.run()

from flask import render_template, request, session, redirect
from flask_cors import cross_origin
from app import app
from spotify import client_id, client_secrect
import spotify

import base64


import requests

redirect_uri = 'http://localhost:5000/callback'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'}  # fake user
    if 'access_token' not in session:

        return render_template('index.html',
                           title='Maddipy',
                           user=user)
    else:
        user_info = spotify.get_user_info()
        session['user_id'] = user_info['id']
        session['display_name'] = user_info['display_name'] \
                                    if user_info['display_name'] else user_info['id']

        session['playlists'] = spotify.get_user_playlists()
        names = [playlist['name'] for playlist in session['playlists']]

        return render_template('home.html',
                                title='Maddipy',
                                display_name= session['display_name'],
                                playlists= session['playlists'],
                                names=names)


@app.route('/duplicate', methods=['POST'])
def duplicate():
    print request.form.values()
    # playlist = request.form['name']
    # print '&&'*80
    # print playlist
    # spotify.create_test_playlist(playlist)
    print '*'*80
    return {'created': 'true'}

@app.route('/callback')
@cross_origin()
def callback():
    auth_code = request.args.get('code')

    if auth_code:
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri
        }

        auth_header = base64.b64encode('%s:%s' % (client_id, client_secrect))
        url = 'https://accounts.spotify.com/api/token'

        r = requests.post(url,
                        headers={'Authorization': 'Basic %s' % auth_header},
                        data=data,
                        allow_redirects=True)

        response = r.json()

        # set session tokens
        session['access_token'] = response['access_token']
        session['token_type'] = response['token_type']
        session['refresh_token'] = response['refresh_token']

        return redirect('/', code=307)

    else:
        return redirect('/')

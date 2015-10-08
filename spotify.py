import base64
import json
import sys
import requests
import spotipy
import spotipy.util as util

from flask import session

client_id = ''
client_secrect = ''
username = 'mmeier2'
new_playlist_name = 'Test Songs'
spotify_base_url = 'https://api.spotify.com/v1/'
auth_header = base64.b64encode('%s:%s' % (client_id, client_secrect))



def refresh_token():
    data = {'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token']
        }
    url = 'https://accounts.spotify.com/api/token'


    r = requests.post(url,
                        headers={'Authorization': 'Basic %s' % auth_header},
                        data=data
                    )

    response = r.json()
    print response
    session['access_token'] = response['access_token']
    session['token_type'] = response['token_type']

def get_user_info():
    r = requests.get(spotify_base_url + 'me',
                        headers={'Authorization': 'Bearer %s' % session['access_token']})
    response = r.json()
    print response

    if 'error' in response and 'expired' in response['error']['message']:
        refresh_token()
        r = requests.get(spotify_base_url + 'me',
                        headers={'Authorization': 'Bearer %s' % session['access_token']})
        response = r.json()

    return response

def get_user_playlists():
    r = requests.get(spotify_base_url + ('users/%s/playlists' % session['user_id']),
                    headers={'Authorization': 'Bearer %s' % session['access_token']})

    response = r.json()
    if 'error' in response and 'expired' in response['error']['message']:
        refresh_token()

    playlists = [{'name': playlist['name'],
                    'id': playlist['id']} for playlist in response['items']]

    return playlists

def add_tracks(spotify, user, playlist_id, tracks):
    print spotify._post("users/%s/playlists/%s/tracks" % (user['id'], playlist_id),
                                payload = tracks)
    place = 's'


def song_doesnt_exists(track, artist_list, names):
    exists =  track['name'] in names

    if not exists:
        return True

    print "$"*80

    artists = track['artists']
    existing_song_artists = [artist for artist in artist_list if track['name'] in artist]
    for existing in existing_song_artists:
        same_artists = True
        existing_artists = existing[track['name']]

        for artist in artists:
            print existing
            print artist['name']
            if artist['name'] not in existing_artists:
                same_artists = False

        if same_artists:
            return False

    return True


def find_songs():
    scope = 'playlist-read-collaborative'
    playlist_name = 'Tropical House Hoes and Hoodrat Shit'

    token = util.prompt_for_user_token(username, scope)

    if token:
        spotify = spotipy.Spotify(auth=token)

        user = spotify.current_user()
        playlists = spotify.user_playlists(user['id'])

        # filter out the playlists we dont want to look for
        playlist = filter(lambda playlist: playlist['name'] == playlist_name, playlists['items'])[0]

        # grab the id to add the new songs to
        new_playlist = filter(lambda playlist: playlist['name'] == new_playlist_name, playlists['items'])[0]
        new_playlist_id = new_playlist['id']
        print new_playlist['name']
        print new_playlist['id'] == playlist['id']

        # get how many songs each has
        playlist_song_count = playlist['tracks']['total']
        new_playlist_song_count = new_playlist['tracks']['total']

        print playlist_song_count
        print new_playlist_song_count

        playlist_tracks = []
        #grab all the songs
        for x in range(0,(playlist_song_count/100)+1):
            offset = 100*x
            print offset
            # the current targeted playlist tracks
            playlist_tracks.extend(spotify.user_playlist_tracks(user['id'],
                                    playlist['id'], offset=offset)['items'])


        print len(playlist_tracks)
        new_playlist_tracks = []
        if new_playlist_song_count:
            for x in range(0,(new_playlist_song_count/100)+1):
                offset = 100*x
                print offset
                # the current test playlist tracks
                new_playlist_tracks.extend(spotify.user_playlist_tracks(user['id'], new_playlist['id'],
                    offset=offset)['items'])

        # create a list of all songs currently in old playlist and
        # in test playlist
        existing_songs = [track['track'] for track in playlist_tracks]
        new_songs = [track['track'] for track in new_playlist_tracks]

        #combine lists
        songs = existing_songs + new_songs

        print len(existing_songs)
        print len(new_songs)
        print len(songs)

        existing_song_ids = []
        existing_song_names = []
        existing_song_artists = []
        playlist_artist_ids = []
        playlist_artist_names = []



        for song in songs:
            # add existing song info for no repeats
            existing_song_ids.append(song['id'])
            existing_song_names.append(song['name'])
            existing_song_artists.append({song['name']: [artist['name'] for artist in song['artists']]})

            for artist in song['artists']:
                if artist['id'] not in playlist_artist_ids:
                    playlist_artist_ids.append(artist['id'])
                    playlist_artist_names.append(artist['name'])

        print sorted(existing_song_names)
        testing = "NONE"

        tracks_to_add = [] # ids of new tracks
        print "looking for %s artists top hits" % len(playlist_artist_ids)
        for index, artist in enumerate(playlist_artist_ids):
            print "INFO: grabbing %s top songs" % playlist_artist_names[index]
            top_tracks = spotify.artist_top_tracks(artist)['tracks']
            for track in top_tracks:
                if track['id'] not in existing_song_ids and \
                    track['uri'] not in tracks_to_add and \
                    song_doesnt_exists(track, existing_song_artists, existing_song_names):
                        if track['name'] == 'Aaj Hoga Muqabla':
                            testing = track['uri']
                        print "not found adding: %s id: %s" % (track['name'],track['id'])
                        tracks_to_add.append(track['uri'])


        new_track_count = len(tracks_to_add)
        print "found %s new songs to add" % new_track_count

        pos = 0

        for x in range(0,new_track_count/100):
            pos = x*100
            print "adding values in range %s-%s" % (pos, pos+100)
            adding_tracks = {'uris': tracks_to_add[pos:pos+100]}
            #add new tracks
            add_tracks(spotify, user, new_playlist_id, adding_tracks)

        pos +=100
        # add the remaining tracks
        print "adding values in range %s-%s" % (pos, new_track_count)
        adding_tracks = {'uris': tracks_to_add[pos:(new_track_count)]}
        print json.dumps(adding_tracks)
        add_tracks(spotify, user, new_playlist_id, adding_tracks)


def create_test_playlist(playlist):
    spotify = spotipy.Spotify(auth=session['access_token'])

    new_playlist_name = "Maddipy suggested: %s" % playlist
    test_playlist = spotify.user_playlist_create(session['user_id'], new_playlist_name)

    print test_playlist

# option = sys.argv[1]

# if option == 'create':
#     create_test_playlist()

# elif option == 'find_songs':
#     find_songs()

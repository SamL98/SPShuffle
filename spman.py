''' Manage the interaction with the Spotify api '''
from json_util import *

import spotipy.util as util
import requests

import os
from os.path import isfile

# Base url for the SP API
base_url = 'https://api.spotify.com/v1/'

id_url = base_url + 'me'

# URL for fetching the library
lib_url = base_url + 'me/tracks'

play_url = id_url + '/player/play'

auth_header = None
user_id = None

def get_userid():
    global user_id

    r = requests.get(id_url, headers=auth_header)
    assert r.status_code == 200, 'Non-200 from user id fetch %d' % r.status_code

    assert r.json(), 'No json user id fetch'
    json = r.json()

    assert 'id' in json, 'No id in user id json'
    user_id = json['id']

def user_url():
    global user_id
    assert user_id, 'User id is none'
    return base_url + 'users/' + user_id

def playlists_url():
    return user_url() + '/playlists'

if auth_header is None:
    # Parameters for SP authentication
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    redirect_uri = 'http://localhost:8080/callback'

    # This opens a web browsers and promps a SP login.
    #
    # After being redirected (to a nonexistent localhost page),
    # copy and paste the url, containing the auth code,
    # into the terminal and spotipy will parse the code and
    # get the resulting OAuth token.
    token = util.prompt_for_user_token(
        'lerner98', 
        'user-read-recently-played user-library-read \
        user-modify-playback-state playlist-modify-public', 
        client_id=client_id, client_secret=client_secret, 
        redirect_uri=redirect_uri)
    assert token, 'Token is nil'

    # HTTP header for SP API authentication
    auth_header = {'Authorization': 'Bearer ' + token}
    get_userid()

# How far into the library we are
library_batch_num = 0

# Max number of library tracks that can be fetched at once
library_batch_size = 50

# Get the user's current library
def get_library():
    if isfile('library.csv'):
        yield load_library_from_file(open('library.csv'))
        return

    global library_batch_num, library_batch_size

    num_tracks = 50
    while num_tracks == 50:
        r = requests.get(
            lib_url,
            params={
                'limit': 50, 
                'offset': library_batch_num * 50 },
            headers=auth_header )
        
        library_batch_num += 1

        assert r.status_code == 200, 'Code %d received' % r.status_code
        assert r.json(), 'No JSON from lib request'
        assert 'items' in r.json(), 'No items key in lib JSON'

        lib_json = r.json()['items']
        tracks = format_tracks(lib_json)
        yield(tracks)
        num_tracks = len(tracks)

def load_library_from_file(f):
    next(f)

    library = []
    for line in f:
        line = line[:-1]
        
        i = line.index(',')
        id, line = line[:i], line[i+1:]
        

        i = line.rindex(',')
        line, duration = line[:i], int(line[i+1:])
        

        i = line.rindex(',')
        title, artist = line[:i], line[i+1:]

        library.append({
            'id': id,
            'title': title,
            'artist': artist,
            'duration': duration
        })

    f.close()
    return library

# Write the library to csv
def save_library(library):
    f = open('library.csv', 'w')

    keys = ['id', 'title', 'artist', 'duration']
    f.write(','.join(keys) + '\n')

    for track in library:
        f.write(','.join([str(track[k]) for k in keys]) + '\n')

    f.close()

def get_container_playlist():
    headers = auth_header
    headers['Content-Type'] = 'application/json'

    r = requests.post(
        playlists_url(),
        json={ 'name': 'Container' },
        headers=headers )
    assert r.status_code == 201 or r.status_code == 200, 'Bad code from playlist create: %d' % r.status_code

    headers = r.headers
    assert 'Location' in headers, 'No Location response header'
    return headers['Location']

def set_track(track, p_url):
    r = requests.put(
        p_url + '/tracks',
        params={ 'uris': 'spotify:track:' + track['id'] },
        headers=auth_header )
    assert r.status_code == 201, 'Bad code from playlist replace: %d' % r.status_code

def play_playlist(p_id):
    r = requests.put(
        play_url,
        json={ 'context_uri': 'spotify:user:' + user_id + ':playlist:' + p_id },
        headers=auth_header
    )
    assert r.status_code == 204, 'Non-204 from play playlist: %d' % r.status_code
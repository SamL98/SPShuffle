''' Utility functions for dealing with JSON '''

# Convert an array of json tracks into an array of dicts
def format_tracks(json):
    return [format_track(tr['track']) for tr in json]

# Format a json object into a track dict
def format_track(json):
    def assert_key(key, msg, js=None):
        if js is None: js = json
        assert key in js, msg
        return js[key]

    title = assert_key('name', 'No name key in JSON')
    artists = assert_key('artists', 'No artists key in JSON')

    assert len(artists) > 0, 'Artists length 0'
    artist = artists[0]
    name = assert_key('name', 'No name for artist', js=artist)

    id = assert_key('id', 'No id for track')
    duration = assert_key('duration_ms', 'No duration for track')

    return { 'title': title,
             'artist': name,
             'id': id,
             'duration': duration }
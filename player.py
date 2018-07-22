from spman import *

from numpy.random import choice as random_choice

p_url = get_container_playlist()
p_id = p_url[p_url.rindex('/') + 1:]

def start_shuffle(library):
    track = random_choice(library)
    set_track(track, p_url)
    play_playlist(p_id)
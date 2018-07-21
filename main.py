import pickle
import statistics
import sys
from collections import defaultdict

import pylast
from spotipy import SpotifyException

SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''
SPOTIFY_REDIRECT_URI = ''
FM_API_KEY = ''
FM_API_SECRET = ''

_fm = None
_spotify = None


def get_sysargs():
    args = sys.argv[1:]
    if len(args) == 3:
        return args
    else:
        print('Usage: lastfm_username lastfm_password spotify_username')
        sys.exit()


fm_username, fm_password, spotify_username = get_sysargs()


def print_stats(username):
    try:
        albums = load(f'{username}_albums')
    except FileNotFoundError:
        albums = get_albums(username)

    albums = tuple(filter(lambda album: album.length, albums.values()))

    artist_streams = defaultdict(int)
    for album in albums:
        artist_streams[album.artist] += album.length
    avg_artist_streams = statistics.mean(artist_streams.values())
    avg_album_streams = statistics.mean(album.listens for album in albums)
    avg_album_length = statistics.mean(album.length for album in albums)

    print(f"{username}'s averages:")
    print(f'\tartist streams: {avg_artist_streams}')
    print(f'\talbum streams: {avg_album_streams}')
    print(f'\talbum length: {avg_album_length} tracks')

    # Sourced from https://www.digitalmusicnews.com/2018/01/16/streaming-music-services-pay-2018/
    payouts = {
        'groove music': 0.02730,
        'napster': 0.01682,
        'tidal': 0.01284,
        'apple music': 0.00783,
        'amazon': 0.0074,
        'deezer': 0.00624,
        'google play': 0.00611,
        'spotify': 0.00397,
        'pandora': 0.00134,
        'youtube': 0.00074
    }

    print('\tpayouts:')
    for service, payout in payouts.items():
        avg_album_value = payout * avg_album_streams
        avg_track_value = avg_album_value / avg_album_length

        print('\t\t{}: ${:.3f}/album, ${:.3f}/track'.format(service, avg_album_value, avg_track_value))


def cache(**kwargs):
    for name, obj in kwargs.items():
        pickle.dump(obj, open(f'{name}.p', 'wb'))


def load(*args):
    ret = []
    for name in args:
        ret.append(pickle.load(open(f'{name}.p', 'rb')))
    if len(args) == 1:
        return ret[0]
    return ret


def get_albums(username):
    try:
        not_on_spotify = load('not_on_spotify')
    except FileNotFoundError:
        not_on_spotify = set()

    fm = get_lastfm_network(fm_username, fm_password)
    recent_tracks = fm.get_user(username).get_recent_tracks(limit=None)

    albums = {}
    for played_track in recent_tracks:
        track = played_track.track
        artist = track.artist.name

        if not played_track.album:
            continue

        if played_track.album not in albums and album_is_on_spotify(artist, played_track.album, not_on_spotify):
            album_tracks = fm.get_album(artist, played_track.album).get_tracks()
            albums[played_track.album] = Album(artist, played_track.album, album_tracks)
        try:
            album = albums[played_track.album]
            album.listen()
        except KeyError:
            pass

    cache(**{f'{username}_albums': albums,
             'not_on_spotify': not_on_spotify})
    return albums


def get_lastfm_network(username, password):
    global _fm
    if not _fm:
        password_hash = pylast.md5(password)
        network = pylast.LastFMNetwork(api_key=FM_API_KEY, api_secret=FM_API_SECRET, username=username,
                                       password_hash=password_hash)
        network.enable_caching('.pylast_cache')
        _fm = network
    return _fm


def album_is_on_spotify(artist, title, not_on_spotify):
    if (artist, title) in not_on_spotify:
        return False

    spotify = get_spotify()

    try:
        results = spotify.search(q=f'{artist} {title}', type='album')
    except SpotifyException:
        return False

    items = results['albums']['items']
    on_spotify = bool(items)
    if not on_spotify:
        not_on_spotify.add((artist, title))
    else:
        print(f'{artist} - {title}')
    return on_spotify


def get_spotify():
    global _spotify
    if not _spotify:
        scope = 'user-read-private'
        from spotipy import util
        token = util.prompt_for_user_token(spotify_username, scope, client_id=SPOTIFY_CLIENT_ID,
                                           client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI)
        if token:
            import spotipy
            _spotify = spotipy.Spotify(auth=token)
        else:
            raise ValueError(f"Can't get token for {spotify_username}")
    return _spotify


class Album:
    def __init__(self, artist=None, title=None, tracks=None):
        self.artist = artist
        self.title = title
        self.length = len(tracks) if tracks else None
        self.listens = 0

    def listen(self):
        self.listens += 1


if __name__ == '__main__':
    print_stats(fm_username)

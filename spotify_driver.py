import getopt
import pprint
import sys
from auth import SECRET, ID

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-modify-playback-state user-read-playback-state streaming ugc-image-upload ' \
        'playlist-modify-private playlist-read-private playlist-modify-public playlist-read-collaborative ' \
        'user-read-private user-read-email user-read-currently-playing user-library-modify user-library-read ' \
        'user-read-playback-position user-read-recently-played user-top-read app-remote-control streaming ' \
        'user-follow-modify user-follow-read'


pp = pprint.PrettyPrinter()


def authentication():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=ID,
                                                   client_secret=SECRET,
                                                   redirect_uri='http://localhost:8000'))
    return sp


def get_playlist(sp, playlist_name):
    playlists = sp.current_user_playlists()
    for idx, item in enumerate(playlists['items']):
        playlist = item['name']
        if playlist == playlist_name:
            return item['uri']


def get_devices(sp):
    devices = sp.devices()
    return devices['devices']



def get_cl_opts(argv):
    try:
        opts, args = getopt.getopt(argv, "hagts:p:d:", ["playlist=", "device=", "shuffle="])
    except getopt.GetoptError:
        print("For help, use: 'spotify_driver.py -h'")
        sys.exit(2)
    return opts


def add_to_lib(sp, current):
    current_track = current
    tracks = [current_track['item']['uri']]
    if True in sp.current_user_saved_tracks_contains(tracks):
        sp.current_user_saved_tracks_delete(tracks)
        return
    sp.current_user_saved_tracks_add(tracks)


def test(sp):
    x = 0
    while(True):
        x = x + 1
        print(x)


def get_active_device(sp):
    devices = get_devices(sp)
    for dev in devices:
        if dev['is_active']:
            return dev['name']

def get_all_playlists(sp):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        print(playlist['name'])


def top_twenty_this_week(sp):
    top_tracks_uri = []
    playlist = get_playlist(sp, "Top 20")
    top_tracks = sp.current_user_top_tracks(limit=20, time_range='short_term')
    for track in top_tracks['items']:
        top_tracks_uri.append(track['uri'])
    sp.playlist_replace_items(playlist_id=playlist, items=top_tracks_uri)
    return playlist


# if __name__ == '__main__':
#     opts = get_cl_opts(sys.argv[1:])
#     sp = authentication()
#     device_name = get_active_device(sp).encode('unicode-escape') if get_active_device(sp) is not None else None
#     current = sp.currently_playing()
#     # pp.pprint(current)
#     pp.pprint(sp.audio_analysis(current['item']['id']))
#     exit(1)
#     context = current['context']['uri'] if current['context'] is not None else None
#     offset = {"uri": current['item']['uri']} if current['context'] is not None else None
#     pos_ms = current['progress_ms']
#     for opt, arg in opts:
#         if opt == '-h':
#             print('-a: add/remove current track to/from library')
#             print('-g: get list of playlists and their uri')
#             print('-p, --playlist <playlist_name>: Name of playlist to start playing')
#             print('-d, --device <device_name>: Name of device to play on. Defaults to active device')
#             print('-s, --shuffle <Boolean>: \'True\' if shuffle on, \'False\' if shuffle off')
#             sys.exit()
#         elif opt == '-t':
#             test(sp)
#             exit()
#         elif opt == '-a':
#             add_to_lib(sp, current)
#             exit()
#         elif opt == '-g':
#             get_all_playlists(sp)
#             exit()
#         elif opt in ('-d', '--device'):
#             device_name = arg
#             d = get_devices(sp)
#             for device in d:
#                 if device['name'] == device_name:
#                     sp.transfer_playback(device_id=device['id'], force_play=True)
#         elif opt in ('-p', '--playlist'):
#             if arg == 'top':
#                 context = top_twenty_this_week(sp)
#             else:
#                 context = get_playlist(sp, arg)
#             offset = None
#             pos_ms = None
#             sp.start_playback(context_uri=context, offset=offset, position_ms=pos_ms)
#         elif opt in ('-s', '--shuffle'):
#             sp.shuffle(state=arg)
from flask import Flask, request
from flask_cors import CORS

import spotify_driver as sd

app = Flask(__name__)
CORS(app)
sp = sd.authentication()
device_name = sd.get_active_device(sp).encode('unicode-escape') if sd.get_active_device(sp) is not None else 'Als iPhone'
current = sp.currently_playing()

context = current['context']['uri'] if current is not None and current['context'] is not None else None
offset = {"uri": current['item']['uri']} if current is not None and current['context'] is not None else None
pos_ms = current['progress_ms'] if current is not None else None

@app.route('/help')
def help_args():
    ret = '/add: add/remove current track to/from library\n'
    ret += '/get: get list of playlists and their uri'
    ret += '/playlist, --playlist <playlist_name>: Name of playlist to start playing\n'
    ret += '/device, --device <device_name>: Name of device to play on. Defaults to active device\n'
    ret += '/shuffle, --shuffle <Boolean>: \'True\' if shuffle on, \'False\' if shuffle off\n'
    return ret


@app.route('/add')
def add_to_library():
    sd.add_to_lib(sp, current)
    return "Success"


@app.route('/get')
def get_playlists():
    ret_plists = {}
    playlists = sp.current_user_playlists()
    for i, playlist in enumerate(playlists['items']):
        ret_plists[i] = playlist['name']
    return ret_plists


@app.route('/playlist', methods=['POST'])
def play_playlist():
    arg = request.form['playlist']
    if arg == 'top':
        context = sd.top_twenty_this_week(sp)
    else:
        context = sd.get_playlist(sp, arg)
    offset = None
    pos_ms = None
    all_devices = sd.get_devices(sp)
    device = next(d for d in all_devices if d['name'] == device_name)
    sp.start_playback(context_uri=context, offset=offset, position_ms=pos_ms, device_id=device['id'])
    return "success"


@app.route('/device', methods=['POST'])
def set_device():
    device_name = request.form['device']
    d = sd.get_devices(sp)
    for device in d:
        if device['name'] == device_name:
            sp.transfer_playback(device_id=device['id'], force_play=True)
    return "success"


@app.route('/shuffle', methods=['POST'])
def shuf():
    s = True if request.form['shuffle'] == 'True' else False
    sp.shuffle(state=s)
    return "success"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10444)
from datetime import datetime

from spotify_api import SpotifyAuthAPI, MY_SPOTIFY_ID


def get_playlist_track_ids(owner_id, playlist_id, client=None):
    client = client or SpotifyAuthAPI()

    playlist_obj = client.get('users/{}/playlists/{}'.format(owner_id, playlist_id))
    track_objs = playlist_obj['tracks']['items']

    track_ids = [track_obj['track']['id'] for track_obj in track_objs]

    return track_ids


def create_playlist_from_track_ids(track_ids, name=None, client=None):
	assert len(track_ids), 'Must put tracks in playlist'

	name = name or datetime.now().strftime('%Y%m%dT%H:%M')
	client = client or SpotifyAuthAPI()
	
	response = client.post(
		'users/{}/playlists'.format(MY_SPOTIFY_ID),
		data={'name': name}
	)

	playlist_id = response['id']

	track_uris = ['spotify:track:{}'.format(tid) for tid in track_ids]

	response = client.post(
		'users/{}/playlists/{}/tracks'.format(MY_SPOTIFY_ID, playlist_id),
		data={'uris': track_uris}
	)
	

if __name__ == '__main__':	
	track_ids = ['63vUX4fixN873tbuAfUbaH', '1LfWibYjk0TD8YNPtzym9A']
	create_playlist_from_track_ids(track_ids, 'testing api')

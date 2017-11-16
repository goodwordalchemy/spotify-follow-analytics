import os

from models import (
	User, Playlist, UserPlaylist, PlaylistTrack,
	get_session, db_connect,
)
from spotify_api import SpotifyAuthAPI, SpotifyException


def _reset():
	engine = db_connect()

	models_to_reset = [UserPlaylist, PlaylistTrack, Playlist]

	for model in models_to_reset:
		model.__table__.drop(engine, checkfirst=True)
	
	for model in reversed(models_to_reset):
		model.__table__.create(engine)
	


def get_db_playlist(session, playlist_id, owner_id):
	playlist = (session
		.query(Playlist)
		.filter_by(
			playlist_id=playlist_id,
			owner_id=owner_id,
		)
		.first()
	)
	return playlist


def populate_playlist_table(reset=False):
	"""
	* Loads user ids from `users` table
	* for each user id, gets playlists
	* save playlists to playlist table
	"""
	if reset:
		_reset()

	session = get_session()
	users = session.query(User).all()

	client = SpotifyAuthAPI()
	
	for i, user in enumerate(users):
		print "caching playlists for user {} of {}".format(i + 1, len(users))

		try:
			playlists = client.get('users/{}/playlists'.format(user.user_id))
		except SpotifyException:
			continue

		for s_playlist in playlists:

			playlist_id = s_playlist['id']
			owner_id = s_playlist['owner']['id']
			name = s_playlist['name']

			playlist = get_db_playlist(session, playlist_id, owner_id)

			if playlist is None:
				playlist = Playlist(
					playlist_id=playlist_id,
					owner_id=owner_id,
					name=name
				)

			playlist.followers.append(user)

			session.add(playlist)
			session.commit()


if __name__ == '__main__':
	populate_playlist_table()

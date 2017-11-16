from models import (
	Playlist, PlaylistTrack, Track, Artist, TrackArtist,
	get_session, db_connect,
)
from spotify_api import SpotifyAuthAPI, SpotifyException

TOO_MANY_SONGS_TO_STORE = 250


def reset():
	engine = db_connect()

	models_to_reset = [PlaylistTrack, TrackArtist, Track, Artist]

	for model in models_to_reset:
		model.__table__.drop(engine, checkfirst=True)
	
	for model in reversed(models_to_reset):
		model.__table__.create(engine)
	
	# TODO upate `too_big` column back to all falses.


def get_playlists_to_process(session):
	processed_playlist_ids = set([pt.playlist_id for pt in session.query(PlaylistTrack)])
	print 'number of processed playlists so far: {}'.format(len(processed_playlist_ids))
	return (session
		.query(Playlist)
		.filter_by(too_big=False)
		.filter(Playlist.playlist_id.notin_(processed_playlist_ids))
	)


def populate_music_entity_tables():
	"""
	* Loads playlist ids from `playlists` table
	* For each playlist id, queries tracks
	* Saves link between track id and playlist id 
	* saves track info to `tracks` table
	* saves track to artist link in `track_to_artist` table
	"""
	session = get_session()
	client = SpotifyAuthAPI()

	playlists = get_playlists_to_process(session)

	playlist_count = playlists.count()

	for i, playlist in enumerate(playlists):
		print "populating playlist {} of {}".format(i + 1, playlist_count)

		playlist_id = playlist.playlist_id
		owner_id = playlist.owner_id

		try:
			s_playlist = client.get('users/{}/playlists/{}/tracks'.format(owner_id, playlist_id))
		except SpotifyException:
			continue
		except UnicodeEncodeError:
			print owner_id.encode('utf-8'), playlist_id.encode('utf-8')
			continue

		if len(s_playlist) > TOO_MANY_SONGS_TO_STORE:
			print "skipping playlist {} because it has {} songs".format(playlist.name.encode('utf-8'), len(s_playlist))

			playlist.too_big = True
			session.add(playlist)
			session.commit()

			continue

		s_playlist = filter(None, [t['track'] for t in s_playlist])

		for k, s_track in enumerate(s_playlist):
			if k % 25 == 0:
				print 'creating track {} of {}'.format(k + 1, len(s_playlist))

			if not s_track.get('id'):
				print 'skipping track name: {} because no track id'.format(s_track.get('name').encode('utf-8'))
				continue
			track = session.query(Track).get(s_track['id'])

			if track is None:
				track = Track(
					track_id=s_track['id'],
					name=s_track['name'],
					album_id=s_track['album']['id'],
					album_name=s_track['album']['name'],
				)

			s_artists = s_track['artists']

			for s_artist in s_artists:
				if not s_artist.get('id'):
					print 'skipping artist name: {} because no artist id'.format(s_artist.get('name'))
					continue
				artist = session.query(Artist).get(s_artist['id'])

				if artist is None:
					artist = Artist(
						artist_id=s_artist['id'],
						name=s_artist['name'],
					)

				track.artists.append(artist)
			playlist.tracks.append(track)

			session.add(playlist)
			session.commit()


if __name__ == '__main__':
	# reset()
	populate_music_entity_tables()

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from db_config import DATABASE_CONFIG

DeclarativeBase = declarative_base()


def create_tables(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


def db_connect():
    """
    Performs database connection using database settings from db_config.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**DATABASE_CONFIG))

def get_session(engine=None):
	if engine is None:
		engine = db_connect()
	Session = sessionmaker(bind=engine)
	return Session()


class UserPlaylist(DeclarativeBase):
	__tablename__ = 'user_playlist'

	user_id = Column(String, ForeignKey('spotify_user.user_id'), primary_key=True)
	playlist_id = Column(String, ForeignKey('playlist.playlist_id'), primary_key=True)


class User(DeclarativeBase):
	__tablename__ = 'spotify_user'

	user_id = Column(String, primary_key=True)
	name = Column(String)
	degree = Column(Integer)

	playlists = relationship(
		'Playlist',
		secondary=UserPlaylist.__table__,
		back_populates='followers',
	)


class PlaylistTrack(DeclarativeBase):
	__tablename__ = 'playlist_track'

	playlist_id = Column(String, ForeignKey('playlist.playlist_id'), primary_key=True)
	track_id = Column(String, ForeignKey('track.track_id'), primary_key=True)


class Playlist(DeclarativeBase):
	__tablename__ = 'playlist'

	playlist_id = Column(String, primary_key=True)
	owner_id = Column(String)
	name = Column(String)
	too_big = Column(Boolean, default=False)

	tracks = relationship(
		'Track',
		secondary=PlaylistTrack.__table__,
		back_populates='playlists',
	)

	followers = relationship(
		'User',
		secondary=UserPlaylist.__table__,
		back_populates='playlists',
	)


class TrackArtist(DeclarativeBase):
	__tablename__ = 'track_artist'

	artist_id = Column(String, ForeignKey('artist.artist_id'), primary_key=True)
	track_id = Column(String, ForeignKey('track.track_id'), primary_key=True)


class Track(DeclarativeBase):
	__tablename__ = 'track'

	track_id = Column(String, primary_key=True)
	name = Column(String)
	album_id = Column(String)
	album_name = Column(String)

	artists = relationship(
		'Artist',
		secondary=TrackArtist.__table__,
		back_populates='tracks',
	)

	playlists = relationship(
		'Playlist',
		secondary=PlaylistTrack.__table__,
		back_populates='tracks',
	)

class Artist(DeclarativeBase):
	__tablename__ = 'artist'

	artist_id = Column(String, primary_key=True)
	name = Column(String)

	tracks = relationship(
		'Track',
		secondary=TrackArtist.__table__,
		back_populates='artists',
	)


def reset():
	engine = db_connect()
	meta = sqlalchemy.MetaData(engine)
	meta.reflect()
	meta.drop_all()
	create_tables(engine)


if __name__ == '__main__':
	reset()

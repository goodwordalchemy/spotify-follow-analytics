import pandas as pd
import networkx as nx

from models import db_connect


def fix_encoding(df):
    return df.applymap(lambda cell: str(cell.encode('utf-8')))


def get_spotify_users(engine):
	spotify_users = pd.read_sql('select * from spotify_user;', engine)[['user_id', 'name']]
	spotify_users = spotify_users.applymap(lambda cell: str(cell.encode('utf-8')))
	spotify_users = spotify_users.set_index('user_id')

	return spotify_users
	
	
def get_follows_table_with_user_info(engine):
	follows = pd.read_csv('data/follows.csv', dtype=str, index_col=0)

	spotify_users = get_spotify_users(engine)
	
	spotify_users_from = spotify_users.copy()
	spotify_users_from.columns = ['{}_from'.format(c) for c in spotify_users_from.columns]

	spotify_users_to = spotify_users.copy()
	spotify_users_to.columns = ['{}_to'.format(c) for c in spotify_users_to.columns]


	follows = follows.join(spotify_users_from, on='from_node')
	follows = follows.join(spotify_users_to, on='to_node')
	
	follows = follows[[c for c in follows.columns if 'degree' not in c]]

	# this user has fake followers.
	# follows = follows[follows.to_node!='ulyssestone']
	# follows = follows[follows.from_node!='ulyssestone']
	
	return follows

def get_follows_graph(engine):
	spotify_user_names = get_spotify_users(engine).name
	follows = get_follows_table_with_user_info(engine)

	follows_graph = nx.from_pandas_dataframe(
		follows,
		'from_node', 
		'to_node', 
		create_using=nx.DiGraph()
	)

	nx.set_node_attributes(
		follows_graph,
		'name',
		dict(spotify_user_names)
	)
	
	return follows_graph


def get_spotify_user_info(engine):
    spotify_users = pd.read_sql('select * from spotify_user;', engine)[['user_id', 'name']]
    
    spotify_users = spotify_users.rename(columns={'name': 'user_name'})
    spotify_users = fix_encoding(spotify_users)
    spotify_users = spotify_users.set_index('user_id')
    
    return spotify_users


def get_track_info(engine):
    track = pd.read_sql('select * from track;', engine)
    
    track = track.rename(columns={'name': 'track_name'})
    track = fix_encoding(track)
    track = track.set_index('track_id')
    
    return track


def get_playlist_info(engine):
    playlist = pd.read_sql('select * from playlist;', engine)

    playlist = playlist.rename(columns={'name': 'playlist_name'})
    playlist = playlist.drop('too_big', axis=1)
    playlist = fix_encoding(playlist)
    playlist = playlist.set_index('playlist_id')
    
    return playlist


def get_playlist_track(engine):
    playlist_track = pd.read_sql('select * from playlist_track;', engine)
    
    playlist_track = fix_encoding(playlist_track)
    
    return playlist_track


def get_user_playlist(engine):
    user_playlist = pd.read_sql('select * from user_playlist;', engine)
    
    user_playlist = fix_encoding(user_playlist)
    
    return user_playlist


def get_user_playlist_track(engine):
    user_playlist = get_user_playlist(engine)
    
    user_info = get_spotify_user_info(engine)
    user_playlist = user_playlist.join(user_info, on='user_id')
    
    playlist_info = get_playlist_info(engine)
    user_playlist = user_playlist.join(playlist_info, on='playlist_id')

    
    playlist_track = get_playlist_track(engine)
    
    track_info = get_track_info(engine)
    playlist_track = playlist_track.join(track_info, on='track_id')
    
    user_track = pd.merge(user_playlist, playlist_track, on='playlist_id')
    
    
    return user_track


if __name__ == '__main__':
	engine = db_connect()

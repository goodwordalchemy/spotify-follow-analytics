import pandas as pd
from sqlalchemy.orm import load_only

from models import User, get_session
from spotify_api import SpotifyAuthAPI, SpotifyException

MY_SPOTIFY_ID = '124292901'
FOLLOWS_FILENAME = 'data/follows.csv'


def get_follows_table():
	return pd.read_csv(FOLLOWS_FILENAME, index_col=0)


def populate_user_table(reset=False):
	"""
	* Loads follows table from csv
	* Restrict to people I follow
	* Get user names
	* save to `spotify_user` table
	"""
	follows = get_follows_table()
	follows_degree = follows.to_node.value_counts()
	my_follows = follows[follows.from_node == MY_SPOTIFY_ID].to_node.unique().tolist() + [MY_SPOTIFY_ID]
	my_follows_degree = follows_degree[follows_degree.index.isin(my_follows)]

	client = SpotifyAuthAPI()
	session = get_session()

	if reset:
		session.query(User).delete()
	else:
		stored_user_ids = [r[0] for r in session.query(User.user_id)]
		my_follows_degree = my_follows_degree[~my_follows_degree.index.isin(stored_user_ids)]
	
	for i, (user_id, degree) in enumerate(my_follows_degree.iteritems()):
		if i % 25 == 0:
			print "saving user {} of {}".format(i + 1, len(my_follows_degree))
		try:
			s_user = client.get('users/{}'.format(user_id))
		except SpotifyException:
			continue

		if not s_user.get('display_name'):
			continue

		display_name = s_user['display_name'].encode('utf-8')

		user = User(user_id=user_id, name=display_name, degree=degree)
		session.add(user)
		session.commit()


if __name__ == '__main__':
	populate_user_table()

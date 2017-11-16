import pickle

def get_user_track_graph():
	with open('data/user_track_graph.pkl', 'r') as handle:
		user_track_graph = pickle.load(handle)
	return user_track_graph


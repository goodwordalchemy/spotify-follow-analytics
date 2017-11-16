from collections import defaultdict
import itertools

from networkx.algorithms import bipartite
from scipy.special import perm
import networkx as nx
import numpy as np
import pandas as pd

from queries import get_track_info



def get_resource_allocation_matrix(graph):
	'''
	Gets the resource allocation matrix W_ij, which represents the the fraction of
	resoure the jth X node transfers to the ith.
	
	w_ij = (1 /  k(x_j)) * sum_l((a_il * a_jl) / k(y_l)
	
	where the indices, l, represent the nodes for each track. 
	'''
	degree_dict = nx.degree(graph)
	
	track_nodes, _ = bipartite.sets(graph)
	
	matrix = {}
	number_of_permutations = int(perm(len(track_nodes), 2))
	for i, (track_i, track_j) in enumerate(itertools.permutations(track_nodes, 2)):
		if i % 1e6 == 0:
			print 'working on user perumation {} of {}'.format(i + 1, number_of_permutations)
		
		summation_term = 0.
		
		user_nodes = set(graph.neighbors(track_i)) | set(graph.neighbors(track_j))
		for user_l in user_nodes:
			summation_term += (
							float(graph.has_edge(track_i, user_l))
							* graph.has_edge(track_j, user_l)
							/ degree_dict[user_l]
			)
		
		matrix[track_i, track_j] = summation_term / degree_dict[track_j]
		
	return matrix


def filter_degree(graph, node_subset=None, threshold=2):
	graph = graph.copy()
		
	degrees = graph.degree()
	
	if node_subset is None:
		node_subset = degrees.keys()
	
	to_remove = [k for k in node_subset if degrees[k] < threshold]
	graph.remove_nodes_from(to_remove)
	
	return graph


def get_user_based_recommendations(graph, matrix, user_id):
	neighbors = graph.neighbors(user_id)
	track_nodes, _ = bipartite.sets(graph)

	uncollected_tracks = set(track_nodes) - set(neighbors)
	
	track_scores = {}
	for i, track in enumerate(uncollected_tracks):
		if i % 5000 == 0 or (i < 100 and i % 50 == 0):
			print 'calculating score for track {} of {}'.format(
				i + 1, len(uncollected_tracks)
			)
		track_scores[track] = sum([matrix[n, track] for n in neighbors
													if n != track])

	recommendations_series = pd.Series(track_scores)
	recommendations_series.name = 'score'
	
	return recommendations_series


def view_recommendations(
	recommendations, number_of_recommendations=20
):
	recommendations_df = recommendations.to_frame()

	track_info = get_track_info(db_connect())
	recommendations_df = recommendations_df.join(track_info)
	
	return (
		recommendations_df
		.sort_index(by='score', ascending=False)
		.head(number_of_recommendations)
	)


def _listify(elem_or_list):
	if isinstance(elem_or_list, basestring):
		elem_or_list = [elem_or_list]
		
	return elem_or_list


def get_track_based_recommendations(graph, matrix, track_ids):
	track_ids = _listify(track_ids)
	track_nodes, _ = bipartite.sets(graph)
	
	track_ids = set(track_ids) & set(track_nodes)
	uncollected_tracks = set(track_nodes) - set(track_ids)
	
	track_scores = {}
	for i, track in enumerate(uncollected_tracks):
		if i % 5000 == 0 or (i < 100 and i % 50 == 0):
			print 'calculating score for track {} of {}'.format(
				i + 1, len(uncollected_tracks)
			)
		track_scores[track] = sum([matrix[n, track] for n in track_ids
													if n != track])

	recommendations_series = pd.Series(track_scores)
	recommendations_series = recommendations_series.sort_values(ascending=False)
	recommendations_series.name = 'score'
	
	return recommendations_series



if __name__ == '__main__':
	from cache import get_user_track_graph
	from models import db_connect
	from spotify_queries import get_playlist_track_ids, create_playlist_from_track_ids
	
	##########
	# my top 100 songs of 2016
	# owner_id = 'spotify'
	# playlist_id = '37i9dQZF1CyJVyuFeAKgRj'

	owner_id = '124292901'
	playlist_id = '3J0xHKkt4PHkdVeLF9tuF9'
	##########

	user_track_graph = get_user_track_graph()

	engine = db_connect()

	track_nodes, _ = bipartite.sets(user_track_graph)
	graph_for_matrix = filter_degree(
		user_track_graph, 
		node_subset=track_nodes, 
		threshold=5
	)
	matrix = get_resource_allocation_matrix(graph_for_matrix)

	playlist_track_ids = get_playlist_track_ids(owner_id, playlist_id)

	track_based_recommendations = get_track_based_recommendations(
		graph_for_matrix, matrix, playlist_track_ids
	)

	print view_recommendations(track_based_recommendations)

	create_playlist_from_track_ids(
		track_based_recommendations.index.tolist()[:50]
	)

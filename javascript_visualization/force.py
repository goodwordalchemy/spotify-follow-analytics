import json
import os

import flask
import networkx as nx
from networkx.readwrite import json_graph
import pandas as pd

from models import db_connect
from queries import get_follows_graph

def prepend_cwd(endpoint):
	full_path = os.path.realpath(__file__)
	path, filename = os.path.split(full_path)
	return os.path.join(path, endpoint)

G = get_follows_graph(db_connect())

# this d3 example uses the name attribute for the mouse-hover value,
# so add a name to each node
# for n in G:
#     G.node[n]['name'] = n
# write json formatted data
d = json_graph.node_link_data(G) # node-link format to serialize
# write json
with open(prepend_cwd('force/force.json'),'w') as handle:
	json.dump(d, handle)
print('Wrote node-link JSON data to force/force.json')

# Serve the file over http to allow for cross origin requests
print os.listdir(prepend_cwd('force'))
app = flask.Flask(__name__, static_folder=prepend_cwd('force/'))

@app.route('/<path:path>')
def static_proxy(path):
  return app.send_static_file(path)
print('\nGo to http://localhost:8000/force.html to see the example\n')
app.run(port=8000)

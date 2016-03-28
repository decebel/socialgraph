import os
import threading
from collections import deque, defaultdict
from Queue import Queue, Full, Empty # thread-safe queue
import threading
import logging
import networkx as nx
from networkx.readwrite import json_graph
from itertools import islice
import json
from timeit import default_timer as timer


log = logging.getLogger('netx')


class Node(object):

	def __init__(self, nodeId, attr):
		self.id = nodeId
		self.attr = attr
		
	def get_id(self):
		return self.id

	def get_attr(self):
		return self.attr

class Edge(object):

	def __init__(self, attr):
		self.attr = attr

	def get_attr(self):
		return self.attr		


class NetX(object):
	"""docstring for NetX"""

	def __init__(self, arg):
		super(NetX, self).__init__()
		self.arg = arg
		self.G = nx.Graph(name='default')
		self.initialLoadComplete = False


	def connect_nodes(self, fromNode, toNode, edge):
		
		try:

			fromNodeId = self.add_node(fromNode)
			toNodeId   = self.add_node(toNode)
			
			if not self.G.has_edge(fromNodeId, toNodeId):
				connectionData = edge.get_attr()
				self.G.add_edge(fromNodeId, toNodeId, connectionData)

		except Exception as ex:
			log.error("error extracting id: {}".format(ex.message))

	def update_edge_info(self, fromNodeId, toNodeId, edgeInfo):
		curr_data = self.G[fromNodeId][toNodeId]
		new_data = edgeInfo.get_attr()
		curr_data.update(new_data)


	def get_edge_info(self, fromNodeId, toNodeId):
		
		if fromNodeId not in self.G:
			raise Exception('node {} not found'.format(fromNodeId))

		if toNodeId not in self.G:
			raise Exception('node {} not found'.format(toNodeId))

		return self.G[fromNodeId][toNodeId]

	def get_simple_path_list(self, sourceId, targetId, cutoff = 6):
		#source = fromNode.get_id()
		#target = toNode.get_id()
		return [path for path in nx.all_simple_paths(self.G, source=sourceId, target=targetId, cutoff = cutoff)]

	def k_shortest_path(self, source, target, k = 6, weight = None):
		"""weight is the key and not the actual weight value"""
		#source = fromNode.get_id()
		#target = toNode.get_id()
		paths = nx.shortest_simple_paths(self.G, source, target, weight = weight)
		return list(islice(paths, k))

	def add_node(self, node):

		nodeId   = node.get_id()
		nodeData = node.get_attr()
		if nodeId not in self.G:
			print "node: {} added with attributes: {}".format(nodeId, nodeData)
			self.G.add_node(nodeId, attr_dict = nodeData)
		else:
			print "node: {} already present with attributes: {}".format(nodeId, nodeData)

		return nodeId


	def add_edge_data(self, fromNodeId, toNodeId, edgeData):
		pass

	def get_underlying(self):
		return self.G

	def get_as_json(self):
		jsonData = json_graph.node_link_data(self.G)
		return jsonData


	def load_from_json(self, fileName='net.json'):
		start = timer()		
		with open(fileName) as json_file:
			json_data = json.load(json_file)
			self.G = json_graph.node_link_graph(json_data)
			self.initialLoadComplete = True
		end = start - timer()
		log.info('time taken to load: {}'.format(end))

	def initial_load_complete(self):
		return self.initialLoadComplete

	def get_quick_status(self):
		info = {}
		info['nodes'] = self.G.number_of_nodes()
		info['edges'] = self.G.number_of_edges()
		return info

	def get_node_names(self):
		return [n for n in self.G.nodes()]

	def get_node_data(self, nodeId):
		return self.G.node[nodeId]

	def get_node_info(self, nodeId):
		return nx.info(self.G, nodeId)
		

	"""
For IPython view

import matplotlib
import matplotlib.pyplot as plt
%matplotlib inline
pos=nx.spring_layout(n) # positions for all nodes
elarge=[(u,v) for (u,v,d) in n.edges(data=True) if d['weight'] <0.5]
esmall=[(u,v) for (u,v,d) in n.edges(data=True) if d['weight'] >=0.5]
nx.draw_networkx_nodes(n,pos,node_size=700)
# edges
nx.draw_networkx_edges(n,pos,edgelist=elarge,
                    width=6)
nx.draw_networkx_edges(n,pos,edgelist=esmall,
                    width=6,alpha=0.5,edge_color='b',style='dashed')

# labels
nx.draw_networkx_labels(n,pos,font_size=20,font_family='sans-serif')

plt.axis('off')
plt.show()
	"""	


"""
To try:
>>> nx.connected_components(G)
[[1, 2, 3], ['spam']]

>>> sorted(nx.degree(G).values())
[0, 1, 1, 2]

>>> nx.clustering(G)
{1: 0.0, 2: 0.0, 3: 0.0, 'spam': 0.0}
"""

def get_test_net():
	sn = NetX('test')
	sn.load_from_json('force.json')
	return sn
		 
def test_initial_load():
	sn = NetX('test')
	sn.load_from_json('force.json')
	status = sn.get_quick_status()
	print "network status: {}".format(status)

def test_graph_json_view():
	sn = get_test_net()
	view = sn.get_as_json()
	print "view: {}".format(view)
	


def test_path_recommendation():
	sn = get_test_net()
	paths = sn.k_shortest_path('alpha', 'beta', 2, weight='weight')
	print "paths: {}".format(paths)

def test_after_updated_weight_recommendation():
	sn = get_test_net()
	
	#update the score 
	edgeInfo = Edge({'weight' : 0.01})
	sn.update_edge_info('alpha', 'beta', edgeInfo)

	#now retrieve the new path
	paths = sn.k_shortest_path('alpha', 'beta', 2, weight='weight')
	print "paths: {}".format(paths)

def test_get_node_names():
	sn = get_test_net()
	names = sn.get_node_names()
	print 'node names: {}'.format(names)

def test_get_node_attributes():
	sn = NetX('newtest')
	node1 = Node('neo', {'type' : 'employee'})
	sn.add_node(node1)
	data = sn.get_node_data('neo')
	print 'node data: {}'.format(data)	
	names = sn.get_node_names()
	print 'node names: {}'.format(names)

	sn2 = get_test_net()
	names = sn2.get_node_names()
	print 'node names: {}'.format(names)

	data = sn2.get_node_data('alpha')
	print 'node data: {}'.format(data)	

def test_get_edge_info():
	sn = get_test_net()
	info = sn.get_edge_info('alpha', 'beta')
	print "edge info: {}".format(info)





def main():
	net = NetX('test')

	test_users = [('as', 'dl', 0.25), ('as', 'go', 0.65), ('go', 'bu', 0.05), ('dl', 'go', 0.45), ('dl', 'bu', 0.6),
	('as', 'bu', 0.9)]

	for pair in test_users:
		(fr, to, wt) = pair
		frmNode = Node(fr, {'name' : fr, 'title' : 1})
		toNode  = Node(to, {'name' : to, 'title': 2})
		edge = Edge({'weight' : wt})
		net.connect_nodes(frmNode, toNode, edge)


	g = net.get_underlying()
	nodes = g.nodes(data=True)
	print "nodes: {}".format(nodes)
	edges  = g.edges()
	print "edges: {}".format(edges)

	serialized = net.get_as_json()
	print "view: {}".format(serialized)
	
	with open('force2.json', 'w') as outfile:
		json.dump(serialized, outfile)	

	(fromId, toId) = ('as', 'bu')
	kPaths = net.k_shortest_path(fromId, toId, 2)
	print "k_shortest_path: {}".format(kPaths)

	allPaths = net.get_simple_path_list(fromId, toId, 2)
	print "allPaths: {}".format(allPaths)

	data = net.get_node_data('as')
	print 'node data: {}'.format(data)	


"""
n.add_node('a')
n.add_node('b')
n.add_node('d')
n.add_node('g')
n.add_edge('a', 'b', weight = 0.1)
n.add_edge('a', 'd', weight = 0.7)
n.add_edge('a', 'g', weight = 0.4)
n.add_edge('b', 'd', weight = 0.3)
n.add_edge('b', 'g', weight = 0.8)
n.add_edge('d', 'g', weight = 0.5)
"""


if __name__ == '__main__':

	logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(levelname)s %(message)s',
					filename='net.log',
					filemode='w')

	# main()
	# test_initial_load()
	# test_graph_json_view()
	# test_path_recommendation()
	# test_after_updated_weight_recommendation()
	# test_get_node_names()
	# test_get_node_attributes()
	test_get_edge_info()
	# test_update_edge_info()

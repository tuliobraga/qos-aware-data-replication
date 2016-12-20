# check if a node is satisfied
def is_node_req_satisfied(n, copies, qosRequirements, shortest_paths_length):
	if not n in copies:
		min_distance = min([shortest_paths_length[n][r] for r in copies])
		return True if qosRequirements[n] >= min_distance else False

	return True

# check if all nodes are satisfied
def is_req_satisfied(nodes, copies, qosRequirements, shortest_paths_length):
	for n in nodes:
		if not is_node_req_satisfied(n, copies, qosRequirements, shortest_paths_length):
			return False

	return True

# get unsatisfied nodes
def get_unsatisfied_nodes(nodes, copies, qosRequirements, shortest_paths_length):
	unsatisfied = []
	for n in nodes:
		if not is_node_req_satisfied(n, copies, qosRequirements, shortest_paths_length):
			unsatisfied.append(n)

	return unsatisfied

# storage + update cost for a replica placement strategy
def sucost(root, replicas, alpha, mu, storage_costs, shortest_paths_length):
	scost = alpha * sum([storage_costs[r] for r in replicas])
	ucost = (1-alpha) * mu * sum([shortest_paths_length[root][r] for r in replicas])
	return scost + ucost

# storage + update cost for a replica placement strategy
def node_sucost(root, node, alpha, mu, storage_costs, shortest_paths_length):
	scost = alpha * storage_costs[node]
	ucost = (1-alpha) * mu * shortest_paths_length[root][node]
	return scost + ucost

# Gen random inputs to test the algorithms. All graphs are connected.
def gen_input(n,m):
	from random import randint
	import networkx as nx

	G = nx.gnm_random_graph(n, m) # gen graph
	while not nx.is_connected(G):
		G = nx.gnm_random_graph(n, m) # gen graph

	R = [randint(0, n) for i in xrange(n)] # gen requirements
	S = [randint(0, 100) for i in xrange(n)] # gen requirements
	return G, R, S
import networkx as nx
from itertools import chain, combinations
from util import is_req_satisfied, sucost, node_sucost

#
# Iterates over all possible replica strategies (replica combinations).
# For those that the QOS-Requirements are satisfied, it calculates their costs.
# Then, find the best strategy looking for the minimum replication cost among those valid ones.
#
# @PARAM G - Graph representing the servers architecture.
# @PARAM storage_costs - A list containing the storage costs of each node.
# @PARAM qosRequirements - A list containing the quality-of-service requirements for each node.
#
# @RETURN best_strategy, min_cost
#
def super_optimum(G, storage_costs, qosRequirements, root, alpha, mu):

	# gen all possible combinations from a list of numbers/nodes
	def all_subsets(ss):
	  return chain(*map(lambda x: combinations(ss, x), range(0, len(ss)+1)))

	# all pair shortest paths
	#shortest_paths = nx.all_pairs_shortest_path(G)
	shortest_paths_length = nx.all_pairs_shortest_path_length(G)

	# create all replica combinations (placement strategies)
	nodes = list(G.nodes_iter())
	nodes.remove(root)
	strategies = all_subsets(nodes)

	# calc sucost for each node
	sucost_mem = {root: 0}
	for n in G.nodes_iter():
		if n != root:
			sucost_mem[n] = node_sucost(root, n, alpha, mu, storage_costs, shortest_paths_length)


	# iterate over all placement strategies
	min_cost = float("inf")
	best_strategy = []
	for strategy in strategies:
		replicas = list(strategy)
		copies = set([root] + replicas)

		# verify if it's a valid solution
		# is all requirements satisfied?
		if is_req_satisfied(G.nodes_iter(), copies, qosRequirements, shortest_paths_length):
			# calc cost
			cost = sum([sucost_mem[r] for r in replicas])

			# check best strategy
			if cost < min_cost:
				min_cost = cost
				best_strategy = replicas

	return best_strategy, min_cost
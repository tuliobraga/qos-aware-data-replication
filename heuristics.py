import networkx as nx
from util import get_unsatisfied_nodes, sucost, node_sucost, is_req_satisfied

# Cover distance heuristic
def cover_abstract(G, storage_costs, qos_requirements, root, alpha, mu, heuristic, coverage_rule):

	# all pairs shortest path length
	shortest_paths_length = nx.all_pairs_shortest_path_length(G)
	copies = [root]

	unsatisfied = get_unsatisfied_nodes(G.nodes_iter(), copies, qos_requirements, shortest_paths_length)
	while len(unsatisfied) > 0:
		minimun = float("inf")
		min_i = False

		for i in unsatisfied:
			ci = coverage_rule(G.nodes_iter(), i, qos_requirements, shortest_paths_length)
			fi = heuristic(i, ci, root, alpha, mu, storage_costs, shortest_paths_length)

			if fi < minimun:
				minimun = fi
				min_i = i

		copies.append(min_i)
		unsatisfied.remove(min_i)
		unsatisfied = get_unsatisfied_nodes(unsatisfied, copies, qos_requirements, shortest_paths_length)

	copies.remove(root)
	cost = sucost(root, copies, alpha, mu, storage_costs, shortest_paths_length)
	return copies, cost

# 1) Calcular matriz dos menores caminhos e atualizar a arvore de distribuicao atraves de Floyd-Warshall.
# 2) Definir no \#0 como raiz e marcar como satisfeito.
# 3) Verificar todos os nos e marcar aqueles que foram satisfeitos.
# 4) Para cada no $i$ nao satisfeito:
# 4.1) Calcular o conjunto de cobertura $c(i)$}
# 4.2) Calcular a funcao heuristica $f(i)$}
# 5) Coloca uma replica no no com menor custo
def cover_distance(G, storage_costs, qos_requirements, root, alpha, mu):
	# Get cover set for node i
	def get_cover_set(nodes, i, qos_requirements, shortest_paths_length):
		return [v for v in nodes if shortest_paths_length[i][v] <= qos_requirements[i]]

	#
	# Calc node i weight in solution
	#
	# @PARAM int i - Node to calc weight.
	# @PARAM list ci - Set of nodes covered by node i.
	# @PARAM int root - Node containing the original copy.
	# @PARAM float alpha - Storage/Update balance variable.
	# @PARAM float mu - Update rate.
	# @PARAM list storage_costs - Storage costs.
	# @PARAM dict shortest_paths_length - all pairs shortest path length.
	#
	# @RETURN float
	#
	def cover_distance_heuristic(i, ci, root, alpha, mu, storage_costs, shortest_paths_length):
		return len(ci) + ((1-alpha)/alpha) * shortest_paths_length[root][i]

	return cover_abstract(G, storage_costs, qos_requirements, root, alpha, mu, cover_distance_heuristic, get_cover_set)

# Cover cost heuristic
def cover_cost(G, storage_costs, qos_requirements, root, alpha, mu):
	# Get cover set for node i
	def get_set_cover(nodes, i, qos_requirements, shortest_paths_length):
		return [v for v in nodes if shortest_paths_length[v][i] <= qos_requirements[v]]

	#
	# Calc node i weight in solution
	#
	# @PARAM int i - Node to calc weight.
	# @PARAM list ci - Set of nodes covered by node i.
	# @PARAM int root - Node containing the original copy.
	# @PARAM float alpha - Storage/Update balance variable.
	# @PARAM float mu - Update rate.
	# @PARAM list storage_costs - Storage costs.
	# @PARAM dict shortest_paths_length - all pairs shortest path length.
	#
	# @RETURN float
	#
	def cover_cost_heuristic(i, ci, root, alpha, mu, storage_costs, shortest_paths_length):
		cost = sucost(root, [i], alpha, mu, storage_costs, shortest_paths_length) / float(len(ci))

	return cover_abstract(G, storage_costs, qos_requirements, root, alpha, mu, cover_cost_heuristic, get_set_cover)
		
def dynamic_cost(G, storage_costs, qos_requirements, root, alpha, mu):
	from collections import Counter
	shortest_paths_length = nx.all_pairs_shortest_path_length(G)
	copies = [root]

	# calc sucost for each node
	sucost_mem = {root: 0}
	for n in G.nodes_iter():
		if n != root:
			sucost_mem[n] = node_sucost(root, n, alpha, mu, storage_costs, shortest_paths_length)

	unsatisfied = get_unsatisfied_nodes(G.nodes_iter(), copies, qos_requirements, shortest_paths_length)

	# calc coverage and make replicas in those that do not have coverage
	while len(unsatisfied) > 0:
		coverage = {}
		coverage_count = {}
		for n in unsatisfied:
			# nodes that covers each unsatisfied node n
			list_cov = [u for u in shortest_paths_length[n] if n != u and shortest_paths_length[n][u] <= qos_requirements[n]]
			if len(list_cov) == 0:
				copies.append(n)
				unsatisfied.remove(n)
			else:
				coverage[n] = list_cov
				coverage_count[n] = len(list_cov)

		# Sort ascending by number of cover nodes. 
		import operator
		sorted_x = sorted(coverage_count.items(), key=operator.itemgetter(1))

		# compute the number of unsatisfied nodes covered by i
		items = []
		for i in coverage:
			items += coverage[i]
		countCovered = dict(Counter(items))

		# select the costless node
		for n, count in sorted_x:
			if n in unsatisfied:
				coef = 1.0
				if n in countCovered.keys():
					coef = float(countCovered[n])

				min_i = sucost_mem[n]/coef
				selected_node = n
				for u in coverage[n]:
					cr = sucost_mem[u]/float(countCovered[u])
					if cr < min_i:
						min_i = cr
						selected_node = u

				copies.append(selected_node)
				unsatisfied = get_unsatisfied_nodes(G.nodes_iter(), copies, qos_requirements, shortest_paths_length)

	copies.remove(root)
	cost = sucost(root, copies, alpha, mu, storage_costs, shortest_paths_length)
	return copies, cost

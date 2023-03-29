from networkx import Graph, draw, all_simple_paths
from syllabify import Pronunciation
from portmanteau_hybrid import words
import matplotlib.pyplot as plt
from collections import Counter
import json

# https://github.com/open-dict-data/ipa-dict
# https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html#networkx.algorithms.simple_paths.all_simple_paths

G = Graph()

# a syllable is a node (saɪ)
# a word is a directed graph of nodes
# saɪ -> ˈkɒ -> ləd -> ʒɪ
# Therefore, my phonetic portmantout is simply the longest path of syllables

print(len(words), 'words')

for word in words:
	for pronunciation in word['pronunciation']:
		full_pronunciation = Pronunciation(pronunciation['IPA'])
		syllables = tuple(full_pronunciation.syllables)
		for i in range(len(syllables) - 1):
			G.add_edge(syllables[i], syllables[i+1])

print('Done adding words.')


current_node = 'pɔːt'
path = ['pɔːt']
while (edges := G.edges(current_node)):
	try:
		# Go to the node with the largest number of
		# edges. Likely a bad heuristic, but we all
		# have to start somewhere.
		node_with_most_edges = max(
			(right for left, right in edges if right not in path),
			key=G.number_of_edges,
		)
		path.append(node_with_most_edges)
		current_node = node_with_most_edges
	except ValueError: # max() arg is an empty sequence, meaning we've run out of nodes
		break

print(len(path))
print(path)
print(Pronunciation.render_syllables(path))

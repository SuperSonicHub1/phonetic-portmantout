import json
import networkx as nx
from networkx.readwrite import json_graph
from word_bank import words_and_pronunciations_en

G = nx.Graph()
for (spelling, pronunciation) in words_and_pronunciations_en:
	syllables = pronunciation.syllables
	if len(syllables) == 1:
		G.add_node(syllables[0])
	else:
		G.add_edges_from((syllables[i], syllables[i+1]) for i in range(len(syllables) - 1))
nx.freeze(G)

with open('data/syllable_map_graph.json', 'w', encoding='utf8') as f:
	json.dump(json_graph.node_link_data(G), f, ensure_ascii=False)

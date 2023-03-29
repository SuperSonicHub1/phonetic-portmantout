import networkx as nx
from networkx.readwrite import json_graph
import json
from syllabify import Pronunciation
from word_bank import words_and_pronunciations_en
from join import join

def first(iterable):
	for item in iterable:
		return item

with open('data/syllable_map_graph.json', encoding='utf-8') as f:
	G = json_graph.node_link_graph(json.load(f))

# Syllables with no edge connections
# AKA one-syllable words where said syllable doesn't
# appear in any other words
dangling_syllables = [
	node
	for node
	in G.nodes
	if G.degree[node] == 0
]

print(len(dangling_syllables), 'dangling syllables.')

# Syllables with no edge connections
# a by-character basis
truly_dangling_syllables = set()

for syllable in dangling_syllables:
	syllable_pron = Pronunciation(syllable)
	success = first(
		filter(
			lambda joining: joining[0] != None,
			(
				(join(syllable_pron, pronunciation, no_overlap=False), word)
				for word, pronunciation
				in words_and_pronunciations_en - {syllable_pron}
			)
		)
	)

	if not success:
		truly_dangling_syllables.add(syllable)

print(len(truly_dangling_syllables))
print(truly_dangling_syllables)

with open('data/truly_dangling_syllables.json', 'w', encoding='utf-8') as f:
	json.dump(truly_dangling_syllables, f, ensure_ascii=False, indent='\t')

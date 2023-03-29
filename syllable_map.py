import json
import networkx as nx
from networkx.exception import NetworkXNoPath
from networkx.readwrite import json_graph
from multiprocessing import Pool
import traceback

# TODO: This is way too slow. We need to be smarter about this.
# # Find parsing bugs
# with open('data/possible-defects.txt', 'w', encoding='utf-8') as f:
# 	from syllabify import PRIMARY_STRESS, SECONDARY_STRESS, SYLLABLE_BREAK
# 	for spelling, pronunciation in words_and_pronunciations:
# 		syllables = pronunciation.syllables
# 		if '' in syllables or 'ˈ' in syllables:
# 			print(syllables, spelling, pronunciation, file=f)
# exit()

def first(iterable):
	for item in iterable:
		return item

def permutations(cdr: str, items):
	for item in items:
		yield cdr, item

with open('data/syllable_map_graph.json', encoding='utf-8') as f:
	G = json_graph.node_link_graph(json.load(f))

def find_paths(syllable: str):
	paths = {}
	for source, target in permutations(syllable, G.nodes()):
		try:
			path = nx.shortest_path(G, source, target)
		except NetworkXNoPath as e:
			path = None
		print(source, target, path)
		paths[target] = path
	return syllable, paths

if __name__ == '__main__':
	with Pool() as pool:
		syllable_map = dict(pool.imap_unordered(find_paths, G.nodes(), chunksize=128))

	with open('data/syllable_map.json', 'w', encoding='utf-8') as f:
		json.dump(syllable_map, f, ensure_ascii=False, indent='\t')

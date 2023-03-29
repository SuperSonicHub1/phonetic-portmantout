import json
import networkx as nx
from networkx.exception import NetworkXNoPath, NodeNotFound
from networkx.readwrite import json_graph
from syllabify import Pronunciation
import random

with open('data/syllable_map_graph.json', encoding='utf-8') as f:
	G = json_graph.node_link_graph(json.load(f))

with open('data/semi_phonoports.finish_line.json', encoding='utf-8') as f:
	particles = set(Pronunciation(particle) for particle in json.load(f))

used_particles = set()

the_big_word = list(particles)[0]
used_particles.add(the_big_word)

while len(used_particles) != len(particles):
	first_syllable = the_big_word.syllables[0]
	last_syllable = the_big_word.syllables[-1]

	first_in_graph = first_syllable in G
	last_in_graph =  last_syllable in G

	if not first_in_graph and not last_in_graph:
		print("We've hit a dead end with", the_big_word, "at", len(the_big_word.syllables), "syllables")
		exit()

	first_has_connections = first_in_graph and G.degree[first_syllable] > 0 
	last_has_connections = last_in_graph and G.degree[last_syllable] > 0

	if not first_has_connections and not last_has_connections:
		print("We've hit a dead end with", the_big_word, "at", len(the_big_word.syllables), "syllables")
		exit()

	new_particle = random.choice(tuple(particles - used_particles))
	new_first_syllable = new_particle.syllables[0]
	new_last_syllable = new_particle.syllables[-1]

	new_first_in_graph = new_first_syllable in G
	new_last_in_graph =  new_last_syllable in G

	if not new_first_in_graph and not new_last_in_graph:
		# Mostly one-syllable words
		print(new_particle, "sucks")
		used_particles.add(new_particle)
		continue
	
	new_first_has_connections = new_first_in_graph and G.degree[new_first_syllable] > 0 
	new_last_has_connections = new_last_in_graph and G.degree[new_last_syllable] > 0

	if not new_first_has_connections and not new_last_has_connections:
		# May be ignoring perfectly good words, but I don't care
		print(new_particle, "sucks")
		used_particles.add(new_particle)
		continue
	
	if first_in_graph and first_has_connections and new_last_in_graph and new_last_has_connections:
		try:
			path = nx.shortest_path(G, new_last_syllable, first_syllable)
			the_big_word = Pronunciation(
				Pronunciation.render_syllables(
					new_particle.syllables[:-1]
					+ path  
					+ the_big_word.syllables[1:]
				)
			)
			used_particles.add(new_particle)
			print("New addition: ", the_big_word)
			print(len(particles - used_particles), "particles left")
			continue
		except NetworkXNoPath as e:
			print(e)
			pass

	if last_in_graph and last_has_connections and new_first_in_graph and new_first_has_connections:
		try:
			path = nx.shortest_path(G, last_syllable, new_first_syllable)
			the_big_word = Pronunciation(
				Pronunciation.render_syllables(
					the_big_word.syllables[:-1]
					+ path
					+ new_particle.syllables[1:]
				)
			)
			used_particles.add(new_particle)
			print("New addition: ", the_big_word)
			print(len(particles - used_particles), "particles left")
			continue
		except NetworkXNoPath as e:
			print(e)
			pass

print(the_big_word)

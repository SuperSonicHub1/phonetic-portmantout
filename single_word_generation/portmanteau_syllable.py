# This approach kinda sucks for single-syllable words like /bɹoʊ/.
# Perhaps I should combine both approaches?
# Also, I need to make a cache for word pronunciations.

import json
import operator
from pprint import pprint
import sys
from difflib import SequenceMatcher
from syllabify import Pronunciation

with open('data/en.dict.v1.json') as f:
	words = json.load(f)

word_dict = {
	word['title']: word
	for word in words
}

word = word_dict[sys.argv[1]]
word_id = word['id']

for pronunciation in word['pronunciation']:
	parsed_pronunciaiton = Pronunciation(pronunciation['IPA'])
	print(f"Phonetic portmanteaus of {parsed_pronunciaiton}:")

	matches = []

	for other_word in filter(lambda word: word['id'] != word_id and len(word['title']) > 1, words):
		for other_pronunciation in other_word['pronunciation']:
			other_parsed_pronunciaiton = Pronunciation(other_pronunciation['IPA'])
			syllables = parsed_pronunciaiton.syllables
			other_syllables = other_parsed_pronunciaiton.syllables
			match = SequenceMatcher(None, syllables, other_syllables).find_longest_match()
			if match.size != 0:
				portmanteau = None
				if match.a + match.size == len(syllables) and match.b == 0:
					portmanteau = Pronunciation.render_syllables(syllables[:match.a] + other_syllables)
				elif match.b + match.size == len(other_syllables) and match.a == 0:
					portmanteau = Pronunciation.render_syllables(other_syllables[:match.b] + syllables)
				# Stops matches like diction and dictionary from coming up
				if portmanteau and portmanteau != parsed_pronunciaiton.pronunciation and portmanteau != other_parsed_pronunciaiton.pronunciation:
					matches.append((word, other_word, portmanteau, match.size))

	# Sort by length of match
	matches = sorted(matches, key=operator.itemgetter(3), reverse=True)
	
	for (word, other_word, portmanteau, size) in matches:
		print(f'Portmanteau found for words {word["title"]!r} and {other_word["title"]!r}: {portmanteau} ({size = })')

	print()
	print('==========')
	print()

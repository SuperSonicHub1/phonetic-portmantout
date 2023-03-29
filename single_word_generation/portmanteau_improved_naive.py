# Even though we now use the improved pronunciations, it still kinda sucks.
# Perhaps matching per syllable might help?
# /	ˈsɛm	.	paɪ	/
# /				paɪd/
# ^ This is a good match because of the great overlap between /paɪ/ and /paɪd/.

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
	parsed_pronunciation = Pronunciation(pronunciation['IPA']).pronunciation[1:-1]
	print(f"Phonetic portmanteaus of {parsed_pronunciation}:")

	matches = []

	for other_word in filter(lambda word: word['id'] != word_id and len(word['title']) > 1, words):
		# We only want single words.
		for other_pronunciation in filter(lambda pronunciation: ' ' not in pronunciation['IPA'], other_word['pronunciation']):
			other_parsed_pronunciation = Pronunciation(other_pronunciation['IPA']).pronunciation[1:-1]

			match = SequenceMatcher(None, parsed_pronunciation, other_parsed_pronunciation).find_longest_match()
			if match.size != 0:
				portmanteau = None
				if match.a + match.size == len(parsed_pronunciation) and match.b == 0:
					portmanteau = parsed_pronunciation[:match.a] + other_parsed_pronunciation
				elif match.b + match.size == len(other_parsed_pronunciation) and match.a == 0:
					portmanteau = other_parsed_pronunciation[:match.b] + parsed_pronunciation
				# Stops matches like diction and dictionary from coming up
				if portmanteau and portmanteau != parsed_pronunciation and portmanteau != other_parsed_pronunciation:
					matches.append((word, other_word, portmanteau, match.size))

	# Sort by length of match
	matches = sorted(matches, key=operator.itemgetter(3), reverse=True)
	
	for (word, other_word, portmanteau, size) in matches:
		print(f'Portmanteau found for words {word["title"]!r} and {other_word["title"]!r}: /{portmanteau}/ ({size = })')

	print()
	print('==========')
	print()

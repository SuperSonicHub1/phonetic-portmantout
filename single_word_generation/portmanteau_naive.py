# While my method of string matching does work, it doesn't take into account at all how syllables work
# For example: 
# Portmanteau found for words 'senpai' and 'intriguing': /ˈsɛmpaɪntɹiːɡɪŋ/ (size=1)
# You can't say that, or at least you need to pick which way you're going to stress the word
# What I need to do next is to syllabify IPA and then combine words together around syllables:
# ˈsɛm	paɪ
# 		paɪ	ˈzɑ.	noʊ
# ˈsɛmpaɪˈzɑ.noʊ
# These sources might be useful

import json
import operator
from pprint import pprint
import sys
from difflib import SequenceMatcher

with open('data/en.dict.v1.json') as f:
	words = json.load(f)

word_dict = {
	word['title']: word
	for word in words
}

word = word_dict[sys.argv[1]]
word_id = word['id']

for pronunciation in word['pronunciation']:
	# Get rid of slashes
	ipa = pronunciation['IPA'][1:-1]

	print(f"Phonetic portmanteaus of /{ipa}/:")

	matches = []

	for other_word in filter(lambda word: word['id'] != word_id and len(word['title']) > 1, words):
		for other_pronunciation in other_word['pronunciation']:
			other_ipa = other_pronunciation['IPA'][1:-1]
			match = SequenceMatcher(None, ipa, other_ipa).find_longest_match()
			if match.size != 0:
				portmanteau = None
				if match.a + match.size == len(ipa) and match.b == 0:
					portmanteau = ipa[:match.a] + other_ipa
				elif match.b + match.size == len(other_ipa) and match.a == 0:
					portmanteau = other_ipa[:match.b] + ipa
				# Stops matches like diction and dictionary from coming up
				if portmanteau and portmanteau != ipa and portmanteau != other_ipa:
					matches.append((word, other_word, portmanteau, match.size))

	# Sort by length of match
	matches = sorted(matches, key=operator.itemgetter(3), reverse=True)
	
	for (word, other_word, portmanteau, size) in matches:
		print(f'Portmanteau found for words {word["title"]!r} and {other_word["title"]!r}: /{portmanteau}/ ({size = })')

	print()
	print('==========')
	print()

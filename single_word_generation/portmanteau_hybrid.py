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

def join_on_syllable(pronunciation: Pronunciation, other_pronunciation: Pronunciation):
	syllables = pronunciation.syllables
	other_syllables = other_pronunciation.syllables
	match = SequenceMatcher(None, syllables, other_syllables).find_longest_match()
	if match.size != 0:
		portmanteau = None
		if match.a + match.size == len(syllables) and match.b == 0:
			portmanteau = Pronunciation.render_syllables(syllables[:match.a] + other_syllables)
		elif match.b + match.size == len(other_syllables) and match.a == 0:
			portmanteau = Pronunciation.render_syllables(other_syllables[:match.b] + syllables)
		# Stops matches like diction and dictionary from coming up
		if portmanteau and portmanteau != pronunciation.pronunciation and portmanteau != other_pronunciation.pronunciation:
			return (portmanteau, match.size)

def join_on_segment(pronunciation: Pronunciation, other_pronunciation: Pronunciation):
	pronunciation_text = pronunciation.pronunciation[1:-1]
	other_pronunciation_text = other_pronunciation.pronunciation[1:-1]
	match = SequenceMatcher(None, pronunciation_text, other_pronunciation_text).find_longest_match()
	if match.size != 0:
		portmanteau = None
		if match.a + match.size == len(pronunciation_text) and match.b == 0:
			portmanteau = pronunciation_text[:match.a] + other_pronunciation_text
		elif match.b + match.size == len(other_pronunciation_text) and match.a == 0:
			portmanteau = other_pronunciation_text[:match.b] + pronunciation_text
		# Stops matches like diction and dictionary from coming up
		if portmanteau and portmanteau != pronunciation_text and portmanteau != other_pronunciation_text:
			return (portmanteau, match.size)

if __name__ == "__main__":
	word = word_dict[sys.argv[1]]
	word_id = word['id']

	for pronunciation in word['pronunciation']:
		pronunciation = Pronunciation(pronunciation['IPA'])
		print(f"Phonetic portmanteaus of {pronunciation}:")

		matches = []

		for other_word in filter(lambda word: word['id'] != word_id and len(word['title']) > 1, words):
			for other_pronunciation in other_word['pronunciation']:
				other_pronunciation = Pronunciation(other_pronunciation['IPA'])
				if len(pronunciation.syllables) == 1:
					possible_portmanteau = join_on_segment(pronunciation, other_pronunciation)
					if possible_portmanteau != None:
						match_size = possible_portmanteau[1]
						if match_size < 2:
							break
				else:
					possible_portmanteau = join_on_syllable(pronunciation, other_pronunciation)

				if possible_portmanteau != None:
					matches.append((word, other_word, *possible_portmanteau))

		# Sort by length of match
		matches = sorted(matches, key=operator.itemgetter(3), reverse=True)
		
		for (word, other_word, portmanteau, size) in matches:
			print(f'Portmanteau found for words {word["title"]!r} and {other_word["title"]!r}: {portmanteau} ({size = })')

		print()
		print('==========')
		print()

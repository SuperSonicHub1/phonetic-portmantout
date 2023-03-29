import json
from itertools import chain
from syllabify import Pronunciation

with open('data/third-party/en.dict.v1.json', encoding='utf8') as f:
	words = json.load(f)

with open('data/truly_dangling_syllables.json', encoding='utf8') as f:
	truly_dangling_syllables = json.load(f)

word_dict = {
	word['title']: word
	for word in words
}

# About 1178 duplicates in en.dict.v1.json
words_and_pronunciations_en = frozenset(
	chain.from_iterable(
		(
			(word['title'], Pronunciation(pronunciation['IPA']))
			for pronunciation in word['pronunciation']
			# No phonic phrases ("earth pig" is one syllable; 2719 of them in en.dict.v1.json)
			if ' ' not in pronunciation['IPA']
			# No single characters (157 in en.dict.v1.json)
			and not (
				len(pronunciation['IPA']) <= 3 
				or (len(pronunciation['IPA']) == 4 and 'ː' in pronunciation['IPA'])
			)
		) for word in words
	)
)

words_and_pronunciations_no_truly_dangling = {
	(word, pronunciation)
	for word, pronunciation
	in words_and_pronunciations_en
	if not (len(pronunciation.syllables) == 1 and pronunciation.syllables[0] in truly_dangling_syllables)
}

# with open('data/third-party/ja.json', encoding='utf8') as f:
# 	ja_words = json.load(f)

# words_and_pronunciaitons_ja = frozenset(
# 	chain.from_iterable(
# 		# Words with multiple pronunciations are broken up with ", "
# 		((word, Pronunciation(pronunciation)) for pronunciation in ipa.split(", "))
# 		for word, ipa in ja_words['ja'][0].items() 
# 	)
# )

import json
from join import join
from word_bank import words_and_pronunciations_en as words_and_pronunciations
# from word_bank import words_and_pronunciations_no_truly_dangling as words_and_pronunciations
# from word_bank import words_and_pronunciaitons_ja as words_and_pronunciations
import random

import random

semi_phonoports = []
used_pronunciations = set()

def first(iterable):
	for item in iterable:
		return item

current_pronunciation = [p for p in words_and_pronunciations if p[0] == 'portmanteau'][0]
# https://en.wiktionary.org/wiki/%E9%9E%84%E8%AA%9E#Japanese
# current_pronunciation = [p for p in words_and_pronunciations if p[0] == '鞄語'][0]
used_pronunciations.add(current_pronunciation)
current_semi_phonoport = current_pronunciation[1]

# SPEEDRUN: Only have a few thousand words
words_and_pronunciations = set(random.choices(list(words_and_pronunciations), k=10000))

while len(used_pronunciations) != len(words_and_pronunciations):
	try:
		# """"""best""""""
		best_joining, best_word = first(
			filter(
				lambda joining: joining[0] != None,
				(
					(join(current_semi_phonoport, pronunciation), word)
					for word, pronunciation in words_and_pronunciations - used_pronunciations
				)
			)
		) 
		# Still slow
		# best_joining, best_word = tuple(
		# 	filter(
		# 		lambda joining: joining[0] != None,
		# 		(
		# 			(join(current_semi_phonoport, pronunciation), word)
		# 			for word, pronunciation in words_and_pronunciations - used_pronunciations
		# 		)
		# 	)
		# )[0]
		# Too slow!!!
		# best_joining, best_word = max(
		# 	filter(
		# 		lambda joining: joining[0] != None,
		# 		(
		# 			(join(current_semi_phonoport, pronunciation), word)
		# 			for word, pronunciation in words_and_pronunciations - used_pronunciations
		# 		)
		# 	)
		# )
		current_semi_phonoport = best_joining.new_word
		used_pronunciations.add((best_word, best_joining.right))
		print(f'{len(words_and_pronunciations - used_pronunciations)} pronunciations left',)
	# we've run out of nodes
	except TypeError: # cannot unpack non-iterable NoneType object
	# except IndexError: # tuple index out of range
	# except ValueError: # max() arg is an empty sequence
		print("New word:", current_semi_phonoport)
		semi_phonoports.append(current_semi_phonoport)
		current_pronunciation = random.choice(tuple(words_and_pronunciations - used_pronunciations))
		used_pronunciations.add(current_pronunciation)
		current_semi_phonoport = current_pronunciation[1]
		print(f"{len(semi_phonoports)} semi-phonoports")
		print("===")

# with open('data/semi_phonoports.json', 'w', encoding='utf-8') as f:
# with open('data/semi_phonoports.ja.json', 'w', encoding='utf-8') as f:
with open('data/semi_phonoports.finish_line.json', 'w', encoding='utf-8') as f:
	json.dump([semi_phonoport.pronunciation for semi_phonoport in semi_phonoports], f, ensure_ascii=False, indent='\t')

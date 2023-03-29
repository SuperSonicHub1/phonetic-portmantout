# from word_bank import words_and_pronunciations
# from word_bank import words_and_pronunciations_no_truly_dangling as words_and_pronunciations
from word_bank import words_and_pronunciations_en as words_and_pronunciations
from collections import Counter
import json

# TODO: Syllable density: Most syllables per character

# Put syllables and edges in Counters
syllable_counter = Counter()
syllable_edge_counter = Counter()
number_of_words_with_one_syllable = 0

for word, pronunciation in words_and_pronunciations:
	syllables = pronunciation.syllables
	if (len(syllables) == 1):
		number_of_words_with_one_syllable += 1
	syllable_counter.update(syllables)
	syllable_edge_counter.update([syllables[i] + ' -> ' + syllables[i+1] for i in range(len(syllables) - 1)])

# Print stats
print()
print(len(words_and_pronunciations), 'words')
print(sum(syllable_counter.values()), "syllables")
print(len(syllable_counter), "unique syllables")
print(sum(syllable_counter.values()) / len(words_and_pronunciations), "syllables per word")
print("Most common syllables:", syllable_counter.most_common(5))
print("Most common edges: ", syllable_edge_counter.most_common(5))
print("Syllables that only appear once:", len({syllable: count for syllable, count in syllable_counter.items() if count == 1}))
print("Words with one syllable:", number_of_words_with_one_syllable)

# Print stats to file
with open('data/syllable_count.json', 'w', encoding='utf8') as f:
	json.dump(dict(syllable_counter), f, ensure_ascii=False, indent='\t')
with open('data/syllable_edge_count.json', 'w', encoding='utf8') as f:
	json.dump(dict(syllable_edge_counter), f, ensure_ascii=False, indent='\t')

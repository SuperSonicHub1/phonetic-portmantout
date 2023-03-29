# TODO

## Log
~~Might also be a good idea to slightly lower my standards for what a good word is by allowing for subsets. (e.g. psych and pyschology become pyschology)~~

~~Since I fixed bad data, try parsing it again!~~

Both of the above did a good bit of damage!

~~Look into pruning words that have single syllables with no connections.~~
- Naive approach ("bro" can be connected to stuff) shows 14643 singular syllables!
- 12682 words with one syllable!
- Final results
	- 12682 - 11577 = 1105 words removed!
	- 14643 - 13765 = 878 singular syllables removed

Also figure out whey there are some empty syllables in my particles.
Trace:
```python
('beakish', <Pronunciation self.pronunciation='ˈbiː.kɪʃ', self.original_pronunciation='/ˈbiːkɪʃ/', self.syllables=['ˈbiː', 'kɪʃ']>)
Join(new_word=<Pronunciation self.pronunciation='ˈbɪ.zi..iæ.zəˈbiː.kɪʃ', self.original_pronunciation='ˈbɪ.zi.iæ.zəˈbiː.kɪʃ', self.syllables=['ˈbɪ', 'zi', '', 'iæ', 'zə', 'ˈbiː', 'kɪʃ']>, left=<Pronunciation self.pronunciation='ˈbiː.kɪʃ', self.original_pronunciation='/ˈbiːkɪʃ/', self.syllables=['ˈbiː', 'kɪʃ']>, right=<Pronunciation self.pronunciation='ˈbɪ.zi.iæ.zəˈbiː', self.original_pronunciation='/ˈbɪziæzəˈbiː/', self.syllables=['ˈbɪ', 'zi', 'iæ', 'zə', 'ˈbiː']>, size=1, join_type=<JoinType.SYLLABLE: 3>) busy as a bee
65519 pronunciations left
('beakish', <Pronunciation self.pronunciation='ˈbiː.kɪʃ', self.original_pronunciation='/ˈbiːkɪʃ/', self.syllables=['ˈbiː', 'kɪʃ']>)
Traceback (most recent call last):
  File "c:\Users\Kyle\Documents\phonetic-portmantou\portmanteau_graph.py", line 21, in <module>
    best_joining, best_word = first(
  File "c:\Users\Kyle\Documents\phonetic-portmantou\portmanteau_graph.py", line 11, in first
    for item in iterable:
  File "c:\Users\Kyle\Documents\phonetic-portmantou\portmanteau_graph.py", line 25, in <genexpr>
    (join(current_semi_phonoport, pronunciation), word)
  File "c:\Users\Kyle\Documents\phonetic-portmantou\join.py", line 42, in join
    return join_on_syllable(pronunciation, other_pronunciation, no_overlap)
  File "c:\Users\Kyle\Documents\phonetic-portmantou\join.py", line 58, in join_on_syllable
    return Join(Pronunciation(portmanteau), pronunciation, other_pronunciation, match.size, JoinType.SYLLABLE)
  File "c:\Users\Kyle\Documents\phonetic-portmantou\syllabify.py", line 333, in __init__
    initial = initial_pass(pronunciation)
  File "c:\Users\Kyle\Documents\phonetic-portmantou\syllabify.py", line 148, in initial_pass
    raise Exception("-> ".join([pronunciation, no_slashes, no_parentheses]))
Exception: ˈbɪ.zi..iæ.zəˈbiː.kɪʃ-> ˈbɪ.zi..iæ.zəˈbiː.kɪʃ-> ˈbɪ.zi..iæ.zəˈbiː.kɪʃ
```

Something to experiment might be breaking up words
into their onsets, nuclei and codas instead of just syllables.
Hopefully that will create longer words which means less possible
endings!

"Technolutions" is a portmanteau of "techno" and "solutions."
It works because /no/ and /so/ sound similar.
```
/	ˈtɛk	noʊ	/
		/	sə	ˈljuː	ʃən	/ (English)
		/	sɔ	ly		sjɔ̃/ (French)
```
There's definitely something here.
Use `Segment.distance(self, other)`.
```python
ft.fts("o").distance(ft.fts("ə")) == 4
ft.fts("o").distance(ft.fts("ɔ")) == 2
```

~~Issues with joining:~~
```python
(
	'ˈfeɪkɚ',
	Join(
		new_word=<Pronunciation self.pronunciation='ɪntɚˌfeɪk', self.original_pronunciation='ɪntɚˌfeɪk', self.syllables=['ɪntɚ', 'ˌfeɪk']>,
		left=<Pronunciation self.pronunciation='ˈfeɪkɚ', self.original_pronunciation='ˈfeɪkɚ', self.syllables=['ˈfeɪkɚ']>,
		right=<Pronunciation self.pronunciation='ˈɪntɚˌfeɪs', self.original_pronunciation='/ˈɪntɚˌfeɪs/', self.syllables=['ˈɪntɚ', 'ˌfeɪs']>,
		size=3,
		join_type=<JoinType.SEGMENT: 1>
	),
	'interface'
)
```
~~Shouldn't we get out `/ˈɪntɚˌfeɪkɚ/`?~~

Found the error: my program was still assuming pronunciations had brackets.

## Snippets
Get number of unique syllables:
```python
from syllabify import Pronunciation
from itertools import chain
import json
with open("data/semi_phonoports.json", encoding='utf-8') as f: words = json.load(f)
pronunciations = [Pronunciation(word) for word in words]
[pronunciation for pronunciation in pronunciations if pronunciation.pronunciation.endswith('ˌ')] 
len(set(chain.from_iterable(([p.syllables[0], p.syllables[-1]] for p in pronunciations)))) # 18557
# Ignoring "stranded" words
len(set(chain.from_iterable(([p.syllables[0], p.syllables[-1]] for p in pronunciations if len(p.syllables) > 1)))) # 15943
```

from itertools import chain
# https://github.com/dmort27/panphon
from panphon import FeatureTable
from panphon._panphon import segment_text
from panphon.segment import Segment
import re
from typing import Union

DEBUG = False

SYLLABLE_BREAK = '.'
PRIMARY_STRESS = 'ˈ'
SECONDARY_STRESS = 'ˌ'
LONG = 'ː'
STRESSES = [PRIMARY_STRESS, SECONDARY_STRESS]

ft = FeatureTable()

voiceless_stops = ['p', 'p̪', 't̼', 't', 'ʈ', "c", 'k', 'q', 'ʡ', 'ʔ']
voiced_stops = ['b', 'b̪', 'd̼', 'd', 'ɖ', 'ɟ', 'ɡ', 'ɢ',]
voiceless_stops_intersection = ft.fts_intersection(voiceless_stops)
voiced_stops_intersection = ft.fts_intersection(voiced_stops)
stops = voiced_stops + voiceless_stops
stops_intersection = ft.fts_intersection(stops)
approximants = ['ʋ', 'ɹ', 'ɻ', 'j', 'ɰ', 'ʔ̞']
approximants_intersection = ft.fts_intersection(approximants)
# silibant + non-silibant
voiceless_silibant_fricatives = ['s', 'ʃ', 'ʂ', 'ɕ',]
voiceless_silibant_fricatives_intersection = ft.fts_intersection(voiceless_silibant_fricatives)
voiceless_non_silibant_fricatives = ['ɸ', 'f', 'θ̼', 'θ', 'θ̠', 'ɹ̠̊˔', 'ɻ̊˔', 'ç', 'x', 'χ', 'ħ', 'h', ]
voiceless_non_silibant_fricatives_intersection = ft.fts_intersection(voiceless_non_silibant_fricatives)
voiceless_fricatives = voiceless_silibant_fricatives + voiceless_non_silibant_fricatives
voiced_fricatives = ['z', 'ʒ', 'ʐ', 'ʑ', 'β', 'v', 'ð̼', 'ð', 'ð̠', 'ɹ̠˔', 'ɻ˔', 'ʝ', 'ɣ', 'ʁ', 'ʕ', 'ɦ']
voiceless_fricatives_intersection = ft.fts_intersection(voiceless_fricatives)
voiced_fricatives_intersection = ft.fts_intersection(voiced_fricatives)

# Hack to get around my parser not supporting multiple-letter consonants
MULTI_LETTER_CONSONANTS = {
	# https://en.wikipedia.org/wiki/Voiced_postalveolar_affricate
	('d͡ʒ', 'dʒ'): 'ʤ',
	# https://en.wikipedia.org/wiki/Voiceless_postalveolar_affricate
	("t͡ʃ", "t͜ʃ", 'tʃ'): 'ʧ',
	# https://en.wikipedia.org/wiki/Voiced_alveolar_affricate#Voiced_alveolar_sibilant_affricate
	('d͡z', 'd͜z', 'dz'): 'ʣ',
	# https://en.wikipedia.org/wiki/Voiceless_alveolar_affricate#Voiceless_alveolar_sibilant_affricate
	("t͡s", "t͜s", 'ts'): 'ʦ',
	# Accounting for aspirated consonants that don't have ligatures
	# with <<special>> unrelated characters
	# https://en.wikipedia.org/wiki/Aspirated_consonant
	tuple(['tʰ']): 'ť',
	tuple(['kʰ']): 'ƙ',
	tuple(['pʰ']): 'ƥ',
	tuple(['bʰ']): 'ƀ',
}

# https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart_for_English_dialects#Chart
AAVE_DIPTHONGS = ["ɛə", "eə", "ɒɔ", "ɔʊ", "iə", "ɛɪ", "eɪ", "eə", "ʊu", "ʊu", "äɪ", "äe", "ʌʊ", "ɔʊ", "æɔ", "æə", "iə", "iɤ", "ɛə", "oə", "ɔə", "ɔo", "uə", "ʊə",]
GENERAL_AMERICAN_DIPTHONGS = ["eə", "ɛə", "eɪ", "ɛɪ", "ɪi", "eɪ", "ʊu", "ʉu", "äɪ", "aɪ", "æɪ", "aɪ", "äɪ", "ʌɪ", "ɜɪ", "ɐɪ", "ɔɪ", "oɪ", "oʊ", "ʌʊ", "ɔʊ", "äʊ", "aʊ", "æʊ"]
GENERAL_AUSTRALIAN_DIPTHONGS = ["ɪi", "ɪi", "əi", "ɛɪ", "æɪ", "ɐɪ", "ɐɪ", "äɪ", "ʊu", "ʊ̈ʉ", "ʊ̈ʉ", "əʉ", "ʊu", "ʊ̈ʉ", "ʊ̈ʉ", "əʉ", "äɪ", "ɑe", "ɑe", "ɑe", "ɒe", "oɪ", "ɜʉ", "ɐʉ", "ɐʉ", "äʉ", "ɒʊ", "ɔʊ", "aɔ", "ao", "æɔ", "æo", "æo", "æə", "ɛo", "ɛə", "ɪə", "iə", "iə", "iə", "eə", "eə", "ʊ̈ʉə", ]
RECIEVED_PRONUNCIATION_DIPTHONGS = ["ɪi", "ɛɪ", "eɪ", "ʊu", "aɪ", "äɪ", "ɔɪ", "ɔʊ", "ɔo", "ɪə", "ʊə", 'əʊ', 'äi']
# IT NEVER ENDS!!!!! (see lower comment which is older than this one)
OTHER_DIPTHONGS = [
	'ai', # IJDB /ˈaidjedibi/,
	'əm̩', # ageism /ˈeɪdʒ.ɪz.əm̩/
	'ɑʊ', # outdid /ˈɑʊtdɪd/
	'ɑɪ', # goldeneye /ˈɡɘʊldn̩.ɑɪ/
	'ɘʊ', # # goldeneye /ˈɡɘʊldn̩.ɑɪ/
	'ei', # able-bodiedness /ˈei.bl̩ˌbɑ.did.nəs/
	'ou', # Genoa /dʒɛnˈou.ə/
	'ɪʊ', # ew /ɪʊ̯/
	'əɒ', # eukaryote /juˈkæɹi.əɒt/
	'əɪ', # Ireland [ˈɑɪɚlənd~ˈʌɪɚlənd~ˈəɪɚlənd]
	'au', # autocrator /au̯.to.kɾa.toɾ/
	'ɘʉ', # out /ɘʉt/
	'əu', # LOL /ɛl.əuˈɛl/
	'iʌ', # ambassadorial /æm.bæs.əˈdoɹ.iʌl/
	'əl̩', # vowel /ˈvaʊ.əl̩/
	'ou', # Genoa /ˈdʒɛn.ou.ə/
	'ɔʏ', # Euler [ˈɔʏlɐ]
	'əu', # cameo /ˈkæm.iː.əu/
	'yu', # disuniate /dɪs.yuˈniˌeɪt/
	'ɔi', # oilocracy /ɔilˈɑkɹəsi/
	'ɵɪ', # thick-knee /ˈɵɪk.niː/
	'ɪa', # macchia /mæk.ɪa/
]
DIPTHONGS = set(AAVE_DIPTHONGS + GENERAL_AMERICAN_DIPTHONGS + GENERAL_AUSTRALIAN_DIPTHONGS + RECIEVED_PRONUNCIATION_DIPTHONGS + OTHER_DIPTHONGS)
# print(DIPTHONGS)
# print(DIPTHONGS.issuperset({"oʊ", "aʊ", "aɪ", "eɪ", "ɔɪ"}))
# exit()

# Apparently, I'm creating a comprehensive list of IPA vowels now
random_vowels = [
	'ɝ', # staffordshire's /ˈstæfɝdʃɝz/
]
thongs = '|'.join(list(DIPTHONGS) + ft.all_segs_matching_fts({'syl': 1}) + random_vowels)
ENGLISH_IPA_VOWELS = re.compile(r'(' + thongs + ')ʰ?:?', re.UNICODE)

def split_before(string: str, separator: str) -> list[str]:
	"""
	Split {string} on {separator} but include {separator}.
	"""
	split = string.split(separator)
	add_separator_back = [separator + part if index > 0 else part for (index, part) in enumerate(split)]
	return [part for part in add_separator_back if part]

def join_back(elements: list[str], loners: list[str]) -> list[str]:
	done = False
	while not done:
		join = False

		for index, element in enumerate(elements):
			if element in loners and index + 1 != len(elements):
				elements = [element + elements[index + 1], *elements[index + 2:]]
				join = True
				break

		if join: continue
		else: done = True
	
	return elements

def initial_pass(pronunciation: str) -> list[str]:
	"""
	https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
	Occasionally the stress mark is placed immediately before the
	nucleus of the syllable, after any consonantal onset.
	In such transcriptions, the stress mark does not mark a syllable boundary.
	⟨.⟩ for a syllable break
	⟨ˈ ˌ⟩ for primary and secondary stresses (appears before stressed syllable)
	⟨ˈˈ or ˌˌ⟩ for extra-{strong,weak} stress
	"""
	if pronunciation.startswith("[") or pronunciation.startswith("/"):
		no_slashes = pronunciation[1:-1]
	else:
		no_slashes = pronunciation
	# NOTE: All optional phones are made required
	# TODO: Support optional phones
	no_parentheses = no_slashes.replace("(", '').replace(")", '')

	if PRIMARY_STRESS + SYLLABLE_BREAK in no_parentheses or SECONDARY_STRESS + SYLLABLE_BREAK in no_parentheses:
		print(f"IPA notation doesn't allow stress marks before syllable breaks: {no_parentheses}")
		no_parentheses = (
			no_parentheses
				.replace(PRIMARY_STRESS + SYLLABLE_BREAK, SYLLABLE_BREAK)
				.replace(SECONDARY_STRESS + SYLLABLE_BREAK, SYLLABLE_BREAK)
		)
		print("Changed to:", no_parentheses)
	if SYLLABLE_BREAK * 2 in no_parentheses:
		raise Exception("-> ".join([pronunciation, no_slashes, no_parentheses]))
		print(f"IPA notation doesn't allow one syllable break immediately after another: {no_parentheses}")
		no_parentheses = (
			no_parentheses
				.replace(SYLLABLE_BREAK + SYLLABLE_BREAK, "")
		)
		print("Changed to:", no_parentheses)
	if no_parentheses.endswith(PRIMARY_STRESS) or no_parentheses.endswith(SECONDARY_STRESS):
		print(f"IPA notation doesn't allow stress marks at the end of a word: {no_parentheses}")
		no_parentheses = no_parentheses[:-1]
		print("Changed to:", no_parentheses)
	
	# Hack to get around my parser not supporting multiple-letter consonants
	single_letters = no_parentheses
	for multi_letters, single_letter in MULTI_LETTER_CONSONANTS.items():
		for multi_letter in multi_letters:
			single_letters = single_letters.replace(multi_letter, single_letter)

	split_on_breaks = single_letters.split(SYLLABLE_BREAK)

	split_on_primary_stress = list(chain.from_iterable(
		split_before(part, PRIMARY_STRESS) for part in split_on_breaks
	))
	split_on_secondary_stress = list(chain.from_iterable(
		split_before(part, SECONDARY_STRESS) for part in split_on_primary_stress
	))

	# Connect lone stresses back to reform extra-{strong,weak} stresses
	joined = join_back(split_on_secondary_stress, [PRIMARY_STRESS, SECONDARY_STRESS])
	return joined

def maybe_match(segment: str, features: Union[dict, Segment]) -> bool:
	for (multi_letter, *_), single_letter in MULTI_LETTER_CONSONANTS.items():
		if segment == single_letter:
			segment = multi_letter
		break

	parsed = ft.fts(segment)
	if parsed != None:
		return parsed.match(features)
	else:
		if DEBUG: print("Syllable couldn't be found:", segment)
		return False

def destructure_syllables(parts: list[str]) -> list[str]:
	"""
	https://en.wikipedia.org/wiki/English_phonology#Syllable_structure
	https://linguistics.stackexchange.com/questions/30933/how-to-split-ipa-spelling-into-syllables
	TODO: Document this beast.
	"""
	return_value = []

	for part in parts:
		if DEBUG: print('Initial part', part)
		vowels = sorted(ENGLISH_IPA_VOWELS.finditer(part), key=lambda group: group.start(0), reverse=True)
		if len(vowels) <= 1:
			if DEBUG: print('One or no vowels')
			return_value.append(part)
			continue

		syllables = []
		end = len(part)

		for index, vowel in enumerate(vowels, start=1):
			if DEBUG: print(vowel)
			parsed = None

			if index == len(vowels):
				if DEBUG: print('First syllable')
				parsed = part[:end]
				end = 0
			else:
				vowel_text = vowel.group(0)
				vowel_start = vowel.start(0)
				vowel_end = vowel.end(0)

				behind_one = part[vowel_start - 1]
				behind_two = part[vowel_start - 2 : vowel_start]
				behind_three = part[vowel_start - 3 : vowel_start]


				if not parsed and behind_three and behind_three[0] not in STRESSES:
					reason = ""
					# /s/ plus voiceless stop plus approximant
					if (
						behind_three[0] == 's'
						and maybe_match(behind_three[1], voiceless_stops_intersection)
						and maybe_match(behind_three[2], approximants_intersection)
					):
						reason = '/s/ plus voiceless stop plus approximant'
					# /s/ plus nasal plus approximant
					elif (
						behind_three[0] == 's'
						and maybe_match(behind_three[1], {'nas': 1})
						and maybe_match(behind_three[2], approximants_intersection)
					):
						reason = '/s/ plus nasal plus approximant'
					# /s/ plus voiceless non-sibilant fricative plus approximant
					elif (
						behind_three[0] == 's'
						and maybe_match(behind_three[1], voiceless_non_silibant_fricatives_intersection)
						and maybe_match(behind_three[2], approximants_intersection)
					):
						reason = "/s/ plus voiceless non-sibilant fricative plus approximant"
					
					if reason:
						if DEBUG: print(reason)
						parsed = behind_three + vowel_text + part[vowel_end:end]
						end = vowel_start - 3

				if not parsed and behind_two and behind_two[0] not in STRESSES:
					reason = ''			
					# Stop plus approximant other than /j/
					if (
						behind_two[1] != 'j'
						and maybe_match(behind_two[0], stops_intersection)
						and maybe_match(behind_two[1], approximants_intersection)
					):
						reason = "Stop plus approximant other than /j/"
					# Voiceless fricative or /v/ plus approximant other than /j/
					elif (
						behind_two[1] != 'j'
						and maybe_match(behind_two[0], voiced_fricatives_intersection)
						and maybe_match(behind_two[1], approximants_intersection)
					):
						reason = "Voiceless fricative or /v/ plus approximant other than /j/"
					# Consonant other than /r/ or /w/ plus /j/ (before /uː/ or its modified/reduced forms)
					elif (
						behind_two[0] not in ['r', 'w']
						and maybe_match(behind_two[0], {'syl': -1})
						and behind_two[1] == 'j'
					):
						reason = "Consonant other than /r/ or /w/ plus /j/ (before /uː/ or its modified/reduced forms)"
					# /s/ plus voiceless stop
					elif (
						behind_two[0] == 's'
						and maybe_match(behind_two[1], voiceless_stops_intersection)
					):
						reason = "/s/ plus voiceless stop"
					# /s/ plus nasal other than /ŋ/
					elif (
						behind_two[1] != 'ŋ'
						and behind_two[0] == 's'
						and maybe_match(behind_two[1], {'nas': 1})
					):
						reason = "/s/ plus nasal other than /ŋ/"
					# /s/ plus voiceless non-sibilant fricative
					elif (
						behind_two[0] == 's'
						and maybe_match(behind_two[1], voiceless_non_silibant_fricatives_intersection)
					):
						reason = "/s/ plus voiceless non-sibilant fricative"

					if reason:
						if DEBUG: print(reason)
						parsed = behind_two + vowel_text + part[vowel_end:end]
						end = vowel_start - 2

				if not parsed:
					# All single-consonant phonemes except /ŋ/
					if behind_one and maybe_match(behind_one, {'syl': -1}) and behind_one != 'ŋ':
						if DEBUG: print('All single-consonant phonemes except /ŋ/')
						parsed = behind_one + vowel_text + part[vowel_end:end]
						end = vowel_start - 1
					# No onset
					else:
						if DEBUG: print("No onset")
						parsed = vowel_text + part[vowel_end:end]
						end = vowel_start

			if DEBUG: print(parsed)
			syllables.insert(0, parsed)

		return_value += syllables

	return return_value

class Pronunciation:
	pronunciation: str
	original_pronunciation: str
	syllables: list[str]

	def __init__(self, pronunciation: str) -> None:
		self.original_pronunciation = pronunciation
		
		initial = initial_pass(pronunciation)
		destructured = destructure_syllables(initial)
		self.syllables = destructured 

		self.pronunciation = Pronunciation.render_syllables(destructured)

		# assert len(self.pronunciation) >= len(self.original_pronunciation)

	@staticmethod
	def render_syllables(syllables: list[str]):
		"""
		Convert a list of IPA syllables to a properly-formated IPA pronunciation.
		"""
		final = ''
		for index, syllable in enumerate(syllables):
			# Hack to get around my parser not supporting multiple-letter consonants
			for (multi_letter, *_), single_letter in MULTI_LETTER_CONSONANTS.items():
				syllable = syllable.replace(single_letter, multi_letter)
			if (
				index != 0
				and not syllable.startswith(PRIMARY_STRESS)
				and not syllable.startswith(SECONDARY_STRESS)
			):
				final += SYLLABLE_BREAK
			final += syllable

		return final

	def __repr__(self) -> str:
		return f'<Pronunciation {self.pronunciation=}, {self.original_pronunciation=}, {self.syllables=}>'

	def __str__(self) -> str:
		return f'/{self.pronunciation}/ (from {self.original_pronunciation})'
	
	def __hash__(self) -> int:
		return hash(self.pronunciation)

if __name__ == "__main__":
	DEBUG = False

	psych = '/saɪˈkɒlədʒɪ/'
	tuba = '/ˈtu.bə/'
	secondary = '/ˈsɛkənˌdɛɹi/'
	pneumonoultramicroscopicsilicovolcanoconiosis = '/njuːˌmɒ.nəʊ.ʌl.tɹə.maɪ.kɹəʊˈskɒ.pɪkˌsɪ.lɪ.kəʊ.vɒl.keɪ.nəʊ.kəʊ.niˈəʊ.sɪs/'
	cheeseburgers = "/ˈtʃizbɝɡɝz/"
	staffordshires = "/ˈstæfɝdʃɝz/"
	IJDB = '/ˈaidjedibi/'
	joyant = "/ˈˈdʒɔ.ɪənt/"
	ageism = "/ˈeɪdʒ.ɪz.əm̩/"
	outdid = "/ˈɑʊtdɪd/"
	goldeneye ="/ˈɡɘʊldn̩.ɑɪ/"
	disuniate = '/dɪs.yuˈniˌeɪt/'
	thick_knee = "/ˈɵɪk.niː/"
	Eyak = "/ˈijæk/"
	picture = '/ˈpɪktʃə/'
	article = '[ˈɑːtʰɪkʰəɫ]'
	Japan = '[d͡ʒɪ̈ˈpʰæn]'
	butter_ham = '/bʊtəɹam/'
	permutates = 'ˈpəːmjʊteɪts'
	European = '/ˌjɝəˈpi.ən/'
	print(Pronunciation(psych))
	# print(Pronunciation(tuba))
	# print(Pronunciation(secondary))
	# print(Pronunciation(pneumonoultramicroscopicsilicovolcanoconiosis))
	# print(Pronunciation(cheeseburgers))
	# print(Pronunciation(staffordshires))
	# print(Pronunciation(joyant))
	# print(Pronunciation(ageism))
	# print(Pronunciation(outdid))
	# print(Pronunciation(goldeneye))
	# print(Pronunciation(disuniate))
	# print(Pronunciation(thick_knee))
	# print(Pronunciation(Eyak))
	# print(Pronunciation(picture))
	# print(Pronunciation(article))
	# print(Pronunciation(Japan))
	# print(Pronunciation(butter_ham))
	# print(Pronunciation(permutates))
	# print(Pronunciation(European))

# All single-consonant phonemes except /ŋ/
# ʒɪ
# All single-consonant phonemes except /ŋ/
# ləd
# All single-consonant phonemes except /ŋ/
# kɒ
# saɪˈkɒlədʒɪ

# Oh no, /l/ is a valid onset *and* coda,
# but it should be with /'kal/!
# What's a guy to do...
# Mr. N says I may just need to pick on or the other.
# There's got to be a better way, though...
# For now, I'm just going to leave it be.

# Another issue: /dʒ/ is a single phone...
# Fixed the above:
# /saɪˈkɒ.lə.d͡ʒɪ/ (from /saɪˈkɒlədʒɪ/)
# I think that was the real issue; the pronunciation now looks much more correct.

# Same issue with tʃ
# Fixed.

# Same issue with aspirated consonant:
# https://en.wikipedia.org/wiki/Aspirated_consonant
# Fixed in an ultra-hacky way.
 
# I did it! 
# We'll keep everything below for context.
# For pneumonoultramicroscopicsilicovolcanoconiosis:
# nəʊ -> n.əʊ
# Gotta add all those vowels and dipthongs:
# https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart_for_English_dialects#Chart
# AAVE, GAE, British English, Australian

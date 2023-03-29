from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
from typing import Optional
from syllabify import (
	Pronunciation,
	LONG,
	PRIMARY_STRESS,
	SECONDARY_STRESS,
)
from functools import total_ordering

class JoinType(Enum):
	SEGMENT = 1
	SYLLABLE = 3

@dataclass
@total_ordering
class Join:
	new_word: Pronunciation
	left: Pronunciation
	right: Pronunciation
	size: int
	join_type: JoinType

	def __lt__(self, other):
		if not isinstance(other, Join):
			return NotImplemented
		else:
			return (self.join_type.value * self.size) < (other.join_type.value * other.size)

def join(pronunciation: Pronunciation, other_pronunciation: Pronunciation, no_overlap: bool = False) -> Optional[Join]:
	"""
	no_overlap (bool): stops matches like diction and dictionary from coming up
	We disable no_overlap in the hopes that we can get less particles in exchange for a lower quality word.
	"""
	if pronunciation.pronunciation == other_pronunciation.pronunciation:
		return None
	if len(pronunciation.syllables) == 1:
		return join_on_segment(pronunciation, other_pronunciation, no_overlap)
	else:
		return join_on_syllable(pronunciation, other_pronunciation, no_overlap)

def join_on_syllable(pronunciation: Pronunciation, other_pronunciation: Pronunciation, no_overlap: bool) -> Optional[Join]:
	syllables = pronunciation.syllables
	other_syllables = other_pronunciation.syllables
	match = SequenceMatcher(None, syllables, other_syllables).find_longest_match()
	if match.size != 0:
		portmanteau = None
		if match.a + match.size == len(syllables) and match.b == 0:
			portmanteau = Pronunciation.render_syllables(syllables[:match.a] + other_syllables)
		elif match.b + match.size == len(other_syllables) and match.a == 0:
			portmanteau = Pronunciation.render_syllables(other_syllables[:match.b] + syllables)
		if not portmanteau:
			return None
		if no_overlap and not (portmanteau != pronunciation.pronunciation and portmanteau != other_pronunciation.pronunciation):
			return None
		return Join(Pronunciation(portmanteau), pronunciation, other_pronunciation, match.size, JoinType.SYLLABLE)

def join_on_segment(pronunciation: Pronunciation, other_pronunciation: Pronunciation, no_overlap: bool) -> Optional[Join]:
	pronunciation_text = pronunciation.pronunciation
	other_pronunciation_text = other_pronunciation.pronunciation
	match = SequenceMatcher(None, pronunciation_text, other_pronunciation_text).find_longest_match()
	size = match.size
	slice = pronunciation_text[match.a: match.a + size]
	if PRIMARY_STRESS in slice:
		size -= 1
	if SECONDARY_STRESS in slice:
		size -= 1
	if LONG in slice:
		size -= 1

	if size >= 2:
		portmanteau = None
		if match.a + size == len(pronunciation_text) and match.b == 0:
			portmanteau = pronunciation_text[:match.a] + other_pronunciation_text
		elif match.b + size == len(other_pronunciation_text) and match.a == 0:
			portmanteau = other_pronunciation_text[:match.b] + pronunciation_text
		if not portmanteau:
			return None
		if no_overlap and not (portmanteau != pronunciation_text and portmanteau != other_pronunciation_text):
			return None
		return Join(Pronunciation(portmanteau), pronunciation, other_pronunciation, match.size, JoinType.SEGMENT)

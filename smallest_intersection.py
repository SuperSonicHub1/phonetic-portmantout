from typing import Union
from panphon import FeatureTable
from panphon.segment import Segment
from syllabify import (
	voiceless_stops,
	voiced_stops,
	stops,
	approximants,
	voiceless_silibant_fricatives,
	voiceless_non_silibant_fricatives,
	voiceless_fricatives,
	voiced_fricatives,
)

def maybe_match(segment: str, features: Union[dict, Segment]) -> bool:
	parsed = ft.fts(segment)
	if parsed != None:
		return parsed.match(features)
	else:
		return False

ft = FeatureTable()
def smallest_intersection(phones: list[str]) -> Segment:
	intersection: Segment = ft.fts_intersection(phones)
	# Remove unspecified features
	specified = intersection.specified()
	intersection = Segment(list(specified.keys()), specified)

	while True:
		for feature, _ in intersection.iteritems():
			new_intersection = Segment(intersection.names, intersection.data)
			new_intersection.data.pop(feature)
			new_intersection.names.pop(new_intersection.names.index(feature))

			if all(maybe_match(phone, new_intersection) for phone in phones):
				intersection = new_intersection
				continue
		break

	return intersection

# Tests
# print('stops:', ft.fts_intersection(stops), '->', smallest_intersection(stops))
# print('voiced_stops:', ft.fts_intersection(voiced_stops), '->', smallest_intersection(voiced_stops))
# print('voiceless_stops:', ft.fts_intersection(voiceless_stops), '->', smallest_intersection(voiceless_stops))

print('voiceless fricative or /v/:', smallest_intersection([*voiceless_fricatives, 'v']))
print('approximant:', smallest_intersection(approximants))
print('voiceless stop:', smallest_intersection(voiceless_stops))
print('stop:', smallest_intersection(stops))
print('voiceless non-silibant fricative:', smallest_intersection(voiceless_non_silibant_fricatives))

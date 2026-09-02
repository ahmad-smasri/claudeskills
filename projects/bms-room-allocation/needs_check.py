"""Rows on the HQ floors already read that still want a human eye.

Three reasons a row lands here:
  BLANK  - the unit is on a screen I read but its leader could not be called
  DIFF   - column J is written and disagrees with column D's room number
  NOTE   - written, but the screen and the register describe the room oddly
"""

# units seen on the eight HQ screens read so far whose leader could not be
# resolved to a named room
BLANK = {
 # Basement
 'FCU0001': 'BF-2 endpoint not resolved',
 'FCU0003': 'BF-2 endpoint not resolved',
 'FCU0004': 'BF-2 leader stops on the outer wall, runs left across the plan',
 'FCU0006': 'BF-2 leader stops on the outer wall, runs left across the plan',
 'FCU0007': 'BF-2 leader stops on the outer wall, runs left across the plan',
 'FCU0008': 'BF-2 endpoint not resolved',
 'FCU0009': 'BF-2 endpoint not resolved',
 'FCU0010': 'BF-2 jogs past B.105 and stops just inside B.014; D and H say B.124',
 'FCU0013': 'BF-2 ends in the unnumbered corridor above B.109',
 'VAV0006': 'BF-2 endpoint not resolved',
 # Ground
 'FCU0012': 'GF-1 ends in the unlabelled lift lobby',
 'FCU0016': 'GF-1 leader crossed the whole plan - mis-trace',
 'FCU0014': 'GF-2 endpoint in an unnamed area',
 'FCU0018': 'GF-2 endpoint in an unnamed area',
 'FCU0111': 'GF-2 endpoint in an unnamed area',
 'VAV0020': 'GF-2 no leader picked up',
 'VAV0039': 'GF-2 endpoint in an unnamed area',
 'VAV0040': 'GF-2 no leader picked up',
 'VAV0043': 'GF-2 no leader picked up',
 'VAV0044': 'GF-2 no leader picked up',
 'VAV0047': 'GF-2 endpoint in an unnamed area',
 'VAV0048': 'GF-1 no leader picked up',
}

# written, but the screen says something the register does not
NOTE = {
 'VAV0046': 'screen shows an unnumbered corridor; D says corridor (south east) G.602',
 'VAV0030': 'ends in the unnamed corridor east of G.001-G.004; D says G.CORIDOR',
}

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
 'FCU0004': 'BF-2 leader stops on the outer wall, runs left across the plan',
 'FCU0013': 'BF-2 ends in the unnumbered corridor above B.109',
 # Ground
}

# written, but the screen says something the register does not
NOTE = {
 'VAV0046': 'screen shows an unnumbered corridor; D says corridor (south east) G.602',
 'VAV0030': 'ends in the unnamed corridor east of G.001-G.004; D says G.CORIDOR',
}

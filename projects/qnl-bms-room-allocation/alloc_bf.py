"""What each unit on the QNL basement Zone 1 screens serves, read off the plan.

`(tag, room, screen, note)`. The room is the text the screen itself prints for
the polygon the leader's dot lands in - not the register's wording, so that the
two can be compared. `note` is empty when the leader was unambiguous, and
starts with `!` where the screen puts the unit somewhere column D does not -
the word-overlap test in `report_qnl.py` cannot see those on its own, because
the two rooms share a name (`Receving Area` and `Corridor east of Receving
Area`).

BF = `QNL: Basement Floor-Zone1 Part1 Section1`.

The whole top half of BF is one open space carrying two labels, `Break Out
Area` at the west end and `Tech.Services & Collections Office` at the east,
with no wall between them - checked at 3x with the contrast raised. So the
screen cannot separate B.001A from B.001 for any unit landing there, and every
one of those rows is marked `open` rather than being given one of the two
names. The register splits them; the screen does not contradict that, it just
cannot confirm it.
"""

OPEN = 'Break Out Area / Tech.Services & Collections Office (open plan)'

BF = [
    ('VAV-B-S11-011', OPEN, 'BF', 'open plan - west end'),
    ('VAV-B-S11-012', OPEN, 'BF', 'open plan - west end'),
    ('VAV-B-S11-002', OPEN, 'BF', 'open plan - west end'),
    ('VAV-B-S11-001', OPEN, 'BF', 'open plan - west end'),
    ('VAV-B-S11-003', OPEN, 'BF', 'open plan - west end'),
    ('VAV-B-S11-013', OPEN, 'BF', 'open plan - west end'),
    ('VAV-B-S11-014', OPEN, 'BF', 'open plan - west end'),
    ('VAV-B-S11-004', OPEN, 'BF', 'open plan'),
    ('VAV-B-S11-005', OPEN, 'BF', 'open plan - east end'),
    ('VAV-B-S11-006', OPEN, 'BF', 'open plan - east end'),
    ('VAV-B-S11-007', OPEN, 'BF', 'open plan - east end'),
    ('VAV-B-S11-017', OPEN, 'BF', 'open plan - east end'),
    ('VAV-B-S11-015', OPEN, 'BF', 'open plan - east end'),
    ('VAV-B-S11-016', OPEN, 'BF', 'open plan - east end'),
    ('VAV-B-S11-021', OPEN, 'BF', 'open plan - east end, inside the purple zone'),

    ('VAV-B-S11-024', 'Kitchen', 'BF', ''),
    ('VAV-B-S11-025', 'Storage', 'BF', ''),
    ('VAV-B-S11-026', 'Finance Cooridinator & Business Support officer', 'BF', ''),
    ('VAV-B-S11-028', 'Analog Resource', 'BF', ''),
    ('VAV-B-S11-033', 'Ad Collection', 'BF', ''),
    ('VAV-B-S11-038', 'Procurement SPC', 'BF', ''),
    ('VAV-B-S11-045', 'Receving Area', 'BF', ''),
    ('VAV-B-S11-046', 'Corridor east of Receving Area', 'BF',
     '!right of the Receving Area wall, in the corridor strip with S11-022;'
     ' column D says Receiving Area B.008'),
    ('VAV-B-S11-022', 'Corridor east of Receving Area', 'BF', ''),
    ('VAV-B-S11-030', 'Budget & Payment', 'BF', 'lower band, west of the partition'),
    ('VAV-B-S11-031', 'Budget & Payment', 'BF', 'lower band, west of the partition'),
]

# Leaders that could not be called on this screen. Left out of column J
# entirely - a guess here reads exactly like a reading.
BF_BLANK = {
    'VAV-B-S11-027': 'walker shares an endpoint with S11-015; needs the leader by eye',
    'VAV-B-S11-029': 'leader lost crossing the lower band; register says Digital Resources B.005',
    'VAV-B-S11-032': 'walker shares an endpoint with S11-044',
    'VAV-B-S11-044': 'walker shares an endpoint with S11-032',
    'VAV-B-S11-043': 'leader stops on the Corridor 1 label',
}

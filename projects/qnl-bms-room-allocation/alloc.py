"""What each unit on a QNL BMS screen serves, read off the plan.

`SCREENS[screen] = [(tag, room, note), ...]`, where `room` is the text the
screen itself prints for the polygon the leader's dot lands in - not the
register's wording, so that the two can be compared. `note` is empty when the
leader was unambiguous and starts with `!` where the screen puts the unit
somewhere column D does not; `report_qnl.py` cannot always see those on its own
because the two rooms share a word.

`BLANK[tag]` is a leader that could not be called. Those rows are left out of
column J entirely: a guess there reads exactly like a reading.

Rule followed throughout: a tracer endpoint is written only when the room it
lands in was confirmed by eye on the annotated image. Where the endpoint
disagrees with column D it is confirmed twice - a false difference costs more
than a blank.
"""

# BF: the whole top half is one open space carrying `Break Out Area` at the
# west end and `Tech.Services & Collections Office` at the east with no wall
# between them, checked at 3x with the contrast raised. The register splits
# them B.001A / B.001; the screen cannot confirm that, so those rows are
# written as the open space and reported OPEN rather than counted either way.
OPEN_BF = 'Break Out Area / Tech.Services & Collections Office (open plan)'
OPEN_BF1 = 'Tech.Services & Collection (open plan)'

SCREENS = {
 'BF': [
    ('VAV-B-S11-001', OPEN_BF, 'open plan - west end'),
    ('VAV-B-S11-002', OPEN_BF, 'open plan - west end'),
    ('VAV-B-S11-003', OPEN_BF, 'open plan - west end'),
    ('VAV-B-S11-004', OPEN_BF, 'open plan'),
    ('VAV-B-S11-005', OPEN_BF, 'open plan - east end'),
    ('VAV-B-S11-006', OPEN_BF, 'open plan - east end'),
    ('VAV-B-S11-007', OPEN_BF, 'open plan - east end'),
    ('VAV-B-S11-011', OPEN_BF, 'open plan - west end'),
    ('VAV-B-S11-012', OPEN_BF, 'open plan - west end'),
    ('VAV-B-S11-013', OPEN_BF, 'open plan - west end'),
    ('VAV-B-S11-014', OPEN_BF, 'open plan - west end'),
    ('VAV-B-S11-015', OPEN_BF, 'open plan - east end'),
    ('VAV-B-S11-016', OPEN_BF, 'open plan - east end'),
    ('VAV-B-S11-017', OPEN_BF, 'open plan - east end'),
    ('VAV-B-S11-021', OPEN_BF, 'open plan - east end, inside the purple zone'),
    ('VAV-B-S11-022', 'Corridor east of Receving Area', ''),
    ('VAV-B-S11-024', 'Kitchen', ''),
    ('VAV-B-S11-025', 'Storage', ''),
    ('VAV-B-S11-026', 'Finance Cooridinator & Business Support officer', ''),
    ('VAV-B-S11-028', 'Analog Resource', ''),
    ('VAV-B-S11-030', 'Budget & Payment', 'lower band, west of the partition'),
    ('VAV-B-S11-031', 'Budget & Payment', 'lower band, west of the partition'),
    ('VAV-B-S11-033', 'Ad Collection', ''),
    ('VAV-B-S11-038', 'Procurement SPC', ''),
    ('VAV-B-S11-045', 'Receving Area', ''),
    ('VAV-B-S11-046', 'Corridor east of Receving Area',
     '!right of the Receving Area wall, in the corridor strip with S11-022;'
     ' column D says Receiving Area B.008'),
 ],

 # BF-1: same open Tech Services space at the top; a block of eight small
 # offices in the middle, each named by a label that leads into it from
 # outside the block; and Corridor 4 running down the east side of the purple
 # zone, confirmed by the `Corridor 4` label's own pointer landing in it.
 'BF-1': [
    ('VAV-B-S11-008', OPEN_BF1, ''),
    ('VAV-B-S11-009', OPEN_BF1, ''),
    ('VAV-B-S11-010', OPEN_BF1, ''),
    ('VAV-B-S11-018', OPEN_BF1, ''),
    ('VAV-B-S11-019', OPEN_BF1, ''),
    ('VAV-B-S11-020', OPEN_BF1, ''),
    ('VAV-B-S13-001', 'Meeting Rm', ''),
    ('VAV-B-S13-002', 'Meeting Rm', ''),
    ('VAV-B-S11-037', 'Corridor 4',
     '!dot is in the Corridor 4 strip west of the MV Rm wall, the strip the'
     ' Corridor 4 label points into; column D says Art & Humanities B.023'),
    ('CAV-S13-007', 'Corridor 4', ''),
 ],

 # BF-2: Plant Rm 1 (purple) and Plant Rm 2 (yellow) with a yellow corridor
 # running west from Plant Rm 2 along the south side of Plant Rm 1.
 'BF-2': [
    ('CAV-S12-001', 'Plant Rm 1',
     '!both S12-001 and S12-002 land in Plant Rm 1; column D says CORRIDOR B.061'),
    ('CAV-S12-002', 'Plant Rm 1', ''),
    ('CAV-S12-003', 'Plant Rm 1', ''),
    ('FCU-B-011', 'Plant Rm 1', ''),
    ('FCU-B-012', 'Plant Rm 1', ''),
    ('CAV-S13-001', 'Corridor south of Plant Rm 1', ''),
    ('CAV-S13-002', 'Corridor south of Plant Rm 1', ''),
    ('CAV-S13-010', 'Plant Rm 2', ''),
    ('CAV-S13-011', 'Plant Rm 2', ''),
    ('CAV-S13-012', 'Plant Rm 2',
     '!dot is inside Plant Rm 2 with S13-010 and S13-011;'
     ' column D says Fire Command B.071'),
    ('CAV-S13-006', 'Plant Rm 2 - narrow band along its north wall',
     'the band may be the Corridor 4 column D names; it carries no label here'),
    ('FCU-B-013', 'Plant Rm 2', ''),
    ('FCU-B-014', 'Plant Rm 2', ''),
    ('FCU-B-003', 'IDF', ''),
    ('FCU-B-028', 'Sorting Shelving Rm', ''),
    ('VAV-B-S11-023', 'Unlabelled strip between Plant Rm 1 and Plant Rm 2',
     'the strip carries no label on this screen, so it cannot be matched'
     ' against column D either way'),
 ],
}

BLANK = {
 'VAV-B-S11-027': 'BF: walker shares an endpoint with S11-015',
 'VAV-B-S11-029': 'BF: leader lost crossing the lower band',
 'VAV-B-S11-032': 'BF: endpoint not confirmed by eye - lands away from Ad Collection',
 'VAV-B-S11-043': 'BF: leader stops on the Corridor 1 label',
 'VAV-B-S11-044': 'BF: walker shares an endpoint with S11-032',
 'VAV-B-S11-034': 'BF-1: three walkers converge on the Licensing Expert cell',
 'VAV-B-S11-035': 'BF-1: leader not resolved',
 'VAV-B-S11-036': 'BF-1: three walkers converge on the Licensing Expert cell',
 'VAV-B-S11-039': 'BF-1: three walkers converge on the Licensing Expert cell',
 'VAV-B-S11-040': 'BF-1: two walkers converge on the Social Sciences cell',
 'VAV-B-S11-041': 'BF-1: leader not resolved',
 'VAV-B-S11-042': 'BF-1: three walkers converge on the Licensing Expert cell',
 'CAV-S13-020': 'BF-1: leader ends in unlabelled grey south of ST-01',
 'VAV-B-S13-006': 'BF-1: leader not resolved',
 'FCU-B-036': 'BF-2: traced to Plant Rm 1, but the unclaimed dot inside IT Office'
              ' is the more likely endpoint - needs the leader by eye',
 'FCU-B-027': 'BF-2: leader not resolved',
 'FCU-B-031': 'BF-2: dot is in an unlabelled cell in the riser strip south of'
              ' IT Office; column D says IDF ROOM B.215A',
}

SCREEN_FILE = {k: 'QNL/%s.jpg' % k for k in SCREENS}

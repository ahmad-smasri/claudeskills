"""What each unit on a QNL BMS screen serves, read off the plan.

`SCREENS[screen] = [(tag, room, note), ...]`, where `room` is the text the
screen itself prints for the polygon the leader's dot lands in - not the
register's wording, so that the two can be compared. `note` is empty when the
leader was unambiguous and starts with `!` where the screen puts the unit
somewhere column D does not; `report_qnl.py` cannot always see those on its own
because the two rooms share a word.

`BLANK[tag]` is a leader that could not be called; where the same screen tag
exists on two screens the key names the screen as well. Those rows are left out of
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
OPEN_BF4 = 'Office AD For LIT / Digitization Rm (open plan)'
OPEN_BF5 = 'Digitization / Instruction Outreach (open plan)'
OPEN_BF6 = 'Plant Rm 3 / Corridor 5 (open plan)'
OPEN_FF = 'Info. Literacy Instr.2 / Writing Head (open plan)'
OPEN_FF2 = 'Restaurant / Front Kitchen (open plan)'
OPEN_FF3 = 'Media Studio1 / Storage / Media Studio2 (open plan)'
SF1_WEST = 'Unlabelled open area, west half of Zone 1'
SF1_CIRC = 'Circulation Office / Breakout space (open plan)'
SF1_TRANSL = 'Transl.Spc& Space ED (strip along the south of the cyan zone)'
SF1_YELLOW = 'Libr.Com.Rel. Spo. & Event Spc / Ad.Admin &Planning (yellow zone)'
SF3_CYAN = 'VIP Waiting / VIP Meeting (open cyan zone)'
PZ = ('the screen prints Plant Zone with no P-number, so which plant zone it'
      ' is cannot be checked from it')

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
    ('VAV-B-S11-032', 'Ad Collection', ''),
    ('VAV-B-S11-033', 'Ad Collection', ''),
    ('VAV-B-S11-043', 'Corridor east of Receving Area',
     '!east of the Receving Area wall, in the corridor strip with S11-046 and'
     ' S11-022; column D says Receiving Area B.008'),
    ('VAV-B-S11-044', 'Budget & Payment (lower band)',
     'the dot is in the lower band with S11-030 and S11-031; the partition'
     ' between the cells is only partial, so which cell is not certain.'
     ' Column D says Receiving Area B.008'),
    ('VAV-B-S11-038', 'Procurement SPC', ''),
    ('VAV-B-S11-045', 'Receving Area', ''),
    ('VAV-B-S11-046', 'Corridor east of Receving Area',
     '!right of the Receving Area wall, in the corridor strip with S11-022;'
     ' column D says Receiving Area B.008'),
    ('KEF-B0004', OPEN_BF, 'open plan - west end'),
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
    # the plant icons on this screen
    ('DX-B0001', 'Corridor 4',
     'the dot is in the Corridor 4 strip, one wall west of MV Rm;'
     ' column D says MV ROOM B.081'),
    ('DX-B0003', 'Emergency Lighting Battery Rm',
     'column D says TRANSFORMER ROOM B.082, which is the room north of it'),
    ('DX-B0014', 'Emergency Lighting Battery Rm',
     'column D says TRANSFORMER ROOM B.082, which is the room north of it'),
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
    # the plant icons on this screen
    ('AHU-B0011', 'Plant Rm 1', ''),
    ('AHU-B0012', 'Plant Rm 1', ''),
    ('AHU-B0003', 'Plant Rm 2', ''),
    ('AHU-B0010', 'Plant Rm 2', ''),
    ('EF-BBV0002', 'Plant Rm 2', ''),
    ('EF-B0013', 'Plant Rm 2',
     'the dot is inside Plant Rm 2 with the AHUs, which is where the fan sits;'
     ' column D names Sprinklers Pumps B.072, a room drawn on BF-3, so the two'
     ' are answering different questions'),
    ('EF-B0014', 'Plant Rm 2',
     'the dot is inside Plant Rm 2 with the AHUs, which is where the fan sits;'
     ' column D names Fire Command B.071, a room drawn on BF-3'),
 ],
 # BF-3: Plant Rm 2 with a column of yellow rooms - Fire Cmd over Sprinkler
 # Pump - and a second yellow block split into three cells. The west cell is
 # the one the `Gas Suppression` label points into, the east is Server Rm, and
 # the middle carries no label of its own.
 'BF-3': [
    ('CAV-S13-021', 'Sprinkler Pump', ''),
    ('CAV-S13-008', 'Unlabelled strip north of Fire Cmd',
     'the strip carries no label; column D says CORRIDOR 4 B.035'),
    ('CAV-S13-013', 'Gas Suppression', ''),
    ('CAV-S13-014', 'Cell between Gas Suppression and Server Rm',
     'the middle cell carries no label of its own'),
    ('FCU-B-008', 'Cell between Gas Suppression and Server Rm',
     '!the dot is in the middle cell, one wall east of the cell the Gas'
     ' Suppression label points into; column D says GAS SUPPRESSION ROOM B.087'),
    ('CAV-S13-015', 'Server Rm', ''),
    ('FCU-B-032', 'Shell Space-Special Collection', ''),
    ('FCU-B-033', 'Shell Space-Special Collection', ''),
    ('FCU-B-034', 'Shell Space-Special Collection', ''),
    ('FCU-B-035', 'Shell Space-Special Collection', ''),
 ],

 # BF-4: the north-west of this zone is a grey band labelled `Loading Area`,
 # and the pink band along the top carries both `Office AD For LIT` and
 # `Digitization Rm` with only a blue strip between them, so those two cannot
 # be separated. `Shell Space` is a room of its own, east across a wall.
 'BF-4': [
    ('VAV-B-S14-001', 'Office', ''),
    ('VAV-B-S14-003', 'Loading Area (north-west grey band)',
     '!the dot is in the grey Loading Area band, two walls west of the pink;'
     ' column D says Office AD For LIT B.057'),
    ('CAV-S14-006', 'Pink lobby west of Refrigerated Store', ''),
    ('VAV-B-S14-009', OPEN_BF4, 'open plan - Office AD For LIT end'),
    ('VAV-B-S14-008', OPEN_BF4,
     '!the dot is in the Digitization Rm end of the open band; Shell Space is'
     ' the next room east across a wall, which is what column D says'),
    ('VAV-B-S14-011', OPEN_BF4, 'open plan - Digitization Rm end'),
    ('VAV-B-S14-012', OPEN_BF4, 'open plan - Digitization Rm end'),
    ('VAV-B-S14-044', 'Binding & Preservation Space', ''),
    ('VAV-B-S14-045', 'Binding & Preservation Space', ''),
    ('VAV-B-S14-049', 'Binding & Preservation Space', ''),
    ('VAV-B-S14-050', 'Binding & Preservation Space', ''),
    ('VAV-B-S14-047', 'Fine Binding / Q-Tel Rm',
     'one cell carrying both labels, west of Binding & Preservation Space'),
    # the plant icons on this screen
    ('EF-B0007', 'Loading Area (north-west grey band)', ''),
    ('DX-B0006', 'Loading Area (pink, south-west)',
     'the dot is in the pink Loading Area, which is where the condenser sits;'
     ' column D names HV ROOM B.083, a room drawn on BF-1'),
 ],
 # BF-5: the west half of the zone is one open purple space carrying both
 # `Digitization` and `Instruction Outreach`; the east block is cut into
 # Storage Rm, Technical Services and Instruction Presentation.
 'BF-5': [
    ('VAV-B-S13-007', 'Shipping Clerk', ''),
    ('VAV-B-S13-008', 'Security Store',
     '!the dot is inside the Security Store cell; the screen has no room'
     ' called Security Control Room, which is what column D says'),
    ('VAV-B-S13-003', 'Processing Rm', ''),
    ('VAV-B-S13-004', 'Processing Rm', ''),
    ('CAV-S13-009', 'Storage',
     'the dot sits on the Storage / Security Equip. boundary'),
    ('CAV-S13-004', 'Corridor 2', ''),
    ('CAV-S13-005', 'Corridor 2', ''),
    ('VAV-B-S10-010', 'Technical Services', ''),
    ('VAV-B-S10-011', 'Technical Services', ''),
    ('VAV-B-S10-016', 'Instruction Presentation', ''),
    ('VAV-B-S10-017', 'Instruction Presentation', ''),
    ('VAV-B-S10-024', OPEN_BF5, 'open plan'),
    # the plant icons on this screen
    ('DX-B0010', 'Processing Rm',
     'column D says SECURITY & BMS B.102'),
    ('DX-B0011', 'Security Equip.',
     'column D says ITTIGATION CONTROL ROOM B.046_ITT'),
 ],
 # BF-6: the cyan fill is one AHU zone, not one room - it carries both
 # `Plant Rm 3` and `Corridor 5` and no wall runs between them, so a dot
 # inside it cannot be given to one or the other.
 'BF-6': [
    ('FCU-B-015', OPEN_BF6, 'open plan - Plant Rm 3 end'),
    ('FCU-B-016', OPEN_BF6, 'open plan - Plant Rm 3 end'),
    ('FCU-B-017', OPEN_BF6, 'open plan - Plant Rm 3 end'),
    ('CAV-S14-004', OPEN_BF6, 'open plan - level with the Corridor 5 label'),
 ],

 # BF-7: four units land in the yellow Researchers Reading Area, which is the
 # one room on this screen the walkers resolve cleanly.
 'BF-7': [
    ('VAV-B-S10-020', 'Researchers Reading Area', ''),
    ('VAV-B-S10-021', 'Researchers Reading Area', ''),
    ('VAV-B-S10-022', 'Researchers Reading Area', ''),
    ('VAV-B-S10-023', 'Researchers Reading Area', ''),
 ],
 # BF-8: the purple VIP zone is cut in two by a diagonal wall; only the
 # south-west cell carries the `VIP Majlis` label.
 'BF-8': [
    ('FCU-B-001', 'IDF Rm',
     'the dot is in the first of the small cells along the north-west wall;'
     ' the IDF Rm label sits over the second'),
    ('VAV-B-S15-010', 'Cell north-east of VIP Majlis',
     'the cell carries no label of its own'),
    ('VAV-B-S15-011', 'VIP Majlis', ''),
 ],

 # BF-10: Plant Rm 4 fills the east of this zone; the small rooms along its
 # south wall are Pump Rm 4, IDF and the shafts.
 'BF-10': [
    ('FCU-B-004', 'FM Storage',
     'the dot is at the west wall in the band that carries the FM Storage and'
     ' Storage labels'),
    ('FCU-B-022', 'FM Storage', ''),
    ('FCU-B-023', 'FM Storage', ''),
    ('FCU-B-024', 'PH Plant', ''),
    ('FCU-B-026', 'Misting System', ''),
    ('FCU-B-030', 'Pump Rm 4',
     '!the dot is inside the Pump Rm 4 box; column D says WATER FEATURE'
     ' ROOM B.226'),
    ('FCU-B-018', 'Plant Rm 4', ''),
    ('FCU-B-019', 'Plant Rm 4', ''),
    ('FCU-B-020', 'Plant Rm 4', ''),
    ('FCU-B-021', 'Plant Rm 4', ''),
    ('AHU-B0005', 'Plant Rm 4', ''),
    ('AHU-B0006', 'Plant Rm 4', ''),
    ('AHU-B0007', 'Plant Rm 4', ''),
    ('AHU-B0008', 'Plant Rm 4', ''),
 ],
 # FF: `Info. Literacy Instr.2` and `Writing Head` share one cell with no wall
 # between them. `Rest Rm Women` is printed inside the Computer Class Rm cell
 # but leads out of it to the rest rooms below, so the three units under that
 # text are in the Computer Class Rm.
 'FF': [
    ('VAV-1F-S11-005', 'Info. Literacy Instr.1', ''),
    ('VAV-1F-S11-010', OPEN_FF, 'open plan'),
    ('VAV-1F-S11-019', OPEN_FF,
     '!the dot is in the Info. Literacy Instr.2 / Writing Head cell, two walls'
     ' west of the Computer Class Rm where column D puts it'),
    ('VAV-1F-S11-015', 'Computer Class Rm', ''),
    ('VAV-1F-S11-016', 'Computer Class Rm', ''),
    ('VAV-1F-S11-020', 'Computer Class Rm', ''),
    ('VAV-1F-S11-002', 'Study Rm2', ''),
    ('VAV-1F-S11-003', 'Cell between Study Rm2 and Study Rm 4',
     'the cell carries no label; Study Rm3 labels the large room to the east'),
    ('VAV-1F-S11-022', 'Study Rm 4', ''),
    ('VAV-1F-S11-088', 'Study Rm3',
     '!the dot is inside the Study Rm3 room; column D says CHILDRENS LIBRARY'
     ' SLOPE CORRIDOR L1.023'),
    ('VAV-1F-S15-006', 'Children Library', ''),
    ('VAV-1F-S15-007', 'Children Library', ''),
    ('VAV-1F-S15-008', 'Children Library', ''),
    ('VAV-1F-S15-039S', 'Head Librarian Office',
     '!the dot is in the Head Librarian Office cell, one wall north of the'
     ' Staff Office cell where column D puts it'),
    ('VAV-1F-S15-012', 'Yellow cell south of Staff Office',
     'the cell carries no label of its own; the Staff Office cell is the one'
     ' above it'),
    ('VAV-1F-S15-096', 'Multipurpose Rm', ''),
    ('VAV-1F-S15-097', 'Multipurpose Rm', ''),
    ('CAV-S11-002', 'Grey area by L-1 and Rest Rm',
     'unlabelled; may be the CORRIDOR L1.023 column D names'),
 ],
 # FF-2: the restaurant is one purple space carrying both `Restaurant` and
 # `Front Kitchen`; the rectangle drawn round the two of them is the counter
 # line, not a wall.
 'FF-2': [
    ('CAV-S15-002', OPEN_FF2, 'open plan'),
    ('CAV-S15-005', OPEN_FF2, 'open plan'),
    ('CAV-S15-011', OPEN_FF2, 'open plan'),
    ('CAV-S15-012', OPEN_FF2, 'open plan - by the Front Kitchen label'),
    ('CAV-S15-013', OPEN_FF2, 'open plan'),
    ('CAV-S15-015', OPEN_FF2, 'open plan'),
    ('CAV-S15-016', OPEN_FF2, 'open plan'),
    ('CAV-S15-017', OPEN_FF2, 'open plan'),
    ('FCU-1F-060', OPEN_FF2, 'open plan - by the Front Kitchen label'),
    ('FCU-1F-061', OPEN_FF2, 'open plan'),
    ('FCU-1F-064', OPEN_FF2, 'open plan'),
    ('VAV-1F-S15-098', 'Multipurpose Rm', ''),
    ('FCU-1F-003', 'IDF Rm', ''),
    ('VAV-1F-S15-009', 'Unlabelled purple strip west of the Restaurant',
     'the strip carries no label; column D says CHILDRENS LIBRARY-PRE SCHOOL'
     ' COLLECTION L1.047, which is on the Zone 1 screen'),
    ('VAV-1F-S15-010', 'Unlabelled purple strip west of the Restaurant',
     'the strip carries no label; column D says CHILDRENS LIBRARY-PRE SCHOOL'
     ' COLLECTION L1.047, which is on the Zone 1 screen'),
 ],
 # FF-3: the three media rooms share one purple space with no wall between
 # them, and the two prayer rooms are the halves of one purple block, named by
 # labels that lead in from the grey to the south.
 'FF-3': [
    ('VAV-1F-S15-003', OPEN_FF3, 'open plan - under the Storage label'),
    ('VAV-1F-S15-004', OPEN_FF3, 'open plan - under the Storage label'),
    ('VAV-1F-S15-022', 'Prayer Rm (Female)',
     'the upper half of the purple block, which is where the Prayer Rm'
     ' (Female) pointer lands'),
    ('CAV-S15-019', 'Band south of the Media Studios',
     'the band carries no label; column D says FURNITURE STORE L1.153'),
    ('VAV-1F-S11-087', 'Yellow band at the north-west corner',
     'the band carries no label; column D says CHILDRENS LIBRARY SLOPE'
     ' CORRIDOR L1.023'),
 ],
 # SF-1: the west half of the plan is one open area with no label on it at
 # all, and every unit that lands in it is given a first-floor room number by
 # column D. The cyan zone is cut into cells across the top with one strip
 # running the width of it below, and the strip is the one carrying the
 # Transl.Spc& Space ED label.
 'SF-1': [
    ('VAV-2F-S12-006', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-007', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-008', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-009', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-010', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-011', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-012', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-013', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-014', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-016', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-003', SF1_WEST,
     'the west half of this Zone 1 plan carries no room label at all; column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S12-021', SF1_CIRC, 'open plan'),
    ('VAV-2F-S12-022', SF1_CIRC, 'open plan'),
    ('VAV-2F-S12-026', SF1_CIRC,
     '!the dot is in the open Circulation Office / Breakout space band;'
     ' Group Study Room 5, which column D names, is a cell south of it'),
    ('VAV-2F-S12-029', 'Group Study Rm 7',
     '!the dot is inside the Group Study Rm 7 cell; column D says Group Study'
     ' Room 6 L2.016, the cell one wall west'),
    ('VAV-2F-S13-004', 'Academic Pers. Libraria',
     '!the dot is inside the Academic Pers. Libraria cell; column D says OPEN'
     ' OFFICE L2.025, which is the cell at the west end of the same zone'),
    ('VAV-2F-S13-005', SF1_TRANSL,
     'the strip runs the width of the cyan zone below the cells; column D says'
     ' ACADEMIC PERS. LIBRARIA L2.022, which is one of those cells'),
    ('VAV-2F-S13-006', SF1_TRANSL,
     'the strip runs the width of the cyan zone below the cells; column D says'
     ' ACD PERS LIBRARIAN L2.022, which is one of those cells'),
    ('VAV-2F-S13-012', SF1_TRANSL,
     'column D says CORRIDOR L2; the strip may be that corridor, it is not'
     ' labelled as one'),
    ('VAV-2F-S13-013', SF1_TRANSL,
     'column D says CORRIDOR L2; the strip may be that corridor, it is not'
     ' labelled as one'),
    ('VAV-2F-S13-007', 'Cell east of Academic Pers. Libraria',
     'the cell carries no label; column D says AD ADMIN & PLANNING L2.023,'
     ' which is in the yellow zone to the south'),
    ('VAV-2F-S10-001', SF1_YELLOW, 'column D says GULF MATERIAL L2'),
    ('VAV-2F-S10-002', SF1_YELLOW, 'column D says GULF MATERIAL L2'),
    ('VAV-2F-S10-003', SF1_YELLOW, 'column D says GULF MATERIAL L2'),
    ('VAV-2F-S10-004', SF1_YELLOW,
     'south half of the yellow zone, which carries no label of its own;'
     ' column D says GULF MATERIAL L2'),
    ('VAV-2F-S10-005', SF1_YELLOW,
     'south half of the yellow zone, which carries no label of its own;'
     ' column D says GULF MATERIAL L2'),
 ],
 # SF-3: the cyan zone is one open space carrying VIP Waiting, VIP Meeting and
 # Rest Rm. Every VAV-2F-S14 unit on this screen lands in it, and column D
 # gives all of them first-floor rooms - the same pattern as SF-1.
 'SF-3': [
    ('VAV-2F-S13-008', 'Office Coord', ''),
    ('VAV-2F-S13-001', "Lib. Director's Rm", ''),
    ('VAV-2F-S13-003', 'Service & Lounge', ''),
    ('VAV-2F-S15-002', 'VIP Rm', ''),
    ('VAV-2F-S15-005', 'VIP Rm',
     'the dot is in the pink VIP Rm; column D says MAJLIS-VIP Meeting L2.046,'
     ' and VIP Meeting is printed in the cyan zone to the east'),
    ('VAV-2F-S14-005', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-006', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-007', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-008', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-009', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-010', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-011', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-012', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-013', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-014', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-015', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-017', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-018', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-019', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-020', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
    ('VAV-2F-S14-021', SF3_CYAN,
     'column D gives this unit a first-floor room number (L1.xxx) although the tag and the screen are both second floor'),
 ],
 # SF-6: the auditorium, a block of small study rooms and an open plate. The
 # study block's cells carry no labels of their own - `Group Study Rm` points
 # into its west side from the left and below, `Indv. Study Rm` into its east
 # side from the right - so a unit is given the side its dot is on.
 'SF-6': [
    ('FCU-2F-034', 'Auditorium', ''),
    ('FCU-2F-035', 'Auditorium', ''),
    ('FCU-2F-036', 'Auditorium', ''),
    ('FCU-2F-045', 'Group Study Rm', 'west side of the study block'),
    ('FCU-2F-046', 'Group Study Rm', 'west side of the study block'),
    ('FCU-2F-047', 'Group Study Rm', 'west side of the study block'),
    ('FCU-2F-049', 'Indv. Study Rm', 'east side of the study block'),
    ('FCU-2F-050', 'Indv. Study Rm', 'east side of the study block'),
    ('FCU-2F-051', 'Indv. Study Rm', 'east side of the study block'),
    ('FCU-2F-052', 'Indv. Study Rm', 'east side of the study block'),
    ('FCU-2F-054', 'Lounge area',
     'the dot sits beside the Lounge area label on the open plate; column D'
     ' says Bridge Raised Floor L2.088'),
    ('FCU-2F-055', 'Lounge area',
     'the dot sits beside the Lounge area label on the open plate; column D'
     ' says Bridge Raised Floor L2.088'),
 ],
 # RF-3: the only room label anywhere on the four roof screens. Its pointer
 # runs down-left into the block at the south-west of the plan, and all four
 # fans on this screen land in that block. The screen prints `Plant Zone` with
 # no number, so P.006 against P.007 cannot be checked from it.
 'RF-3': [
    ('SEF-RP0010', 'Plant Zone', PZ),
    ('SEF-RP0011', 'Plant Zone', PZ),
    ('SEF-RP0012', 'Plant Zone', PZ),
    ('EF-RP0003', 'Plant Zone', PZ),
 ],
}

BLANK = {
 'VAV-B-S11-027': 'BF: walker shares an endpoint with S11-015',
 'VAV-B-S11-029': 'BF: leader lost crossing the lower band',
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
 'FCU-B-006': 'BF-3: two walkers converge above the plan edge',
 'FCU-B-007': 'BF-3: traced into Shell Space with FCU-B-035; column D says Sprinklers Pumps',
 'FCU-B-009': 'BF-3: two walkers converge above the plan edge',
 'CAV-S13-003': 'BF-3: leader ends off the plan',
 'FCU-B-037': 'BF-3: leader not resolved',
 'VAV-B-S14-002': 'BF-4: leader not resolved',
 'VAV-B-S14-004': 'BF-4: two walkers converge off the plan',
 'VAV-B-S14-005': 'BF-4: leader not resolved',
 'VAV-B-S14-006': 'BF-4: leader not resolved',
 'VAV-B-S14-007': 'BF-4: leader not resolved',
 'VAV-B-S14-010': 'BF-4: two walkers converge off the plan',
 'VAV-B-S14-013': 'BF-4: leader not resolved',
 'VAV-B-S14-014': 'BF-4: leader not resolved',
 'VAV-B-S14-015': 'BF-4: leader not resolved',
 'VAV-B-S14-016': 'BF-4: leader not resolved',
 'VAV-B-S14-040': 'BF-4: leader not resolved',
 'VAV-B-S14-041': 'BF-4: leader not resolved',
 'VAV-B-S14-042': 'BF-4: leader not resolved',
 'VAV-B-S14-043': 'BF-4: leader not resolved',
 'VAV-B-S14-046': 'BF-4: leader not resolved',
 'VAV-B-S14-048': 'BF-4: dot is in the grey south of the pink, not in a named room',
 'VAV-B-S14-051': 'BF-4: dot is in the grey south of the pink, not in a named room',
 'CAV-S15-002 (BF-4)': 'BF-4: leader not resolved',
 'CAV-S15-003 (BF-4)': 'BF-4: leader not resolved',
 'CAV-S14-007': 'BF-4: leader not resolved',
 'FCU-B-010': 'BF-5: leader ends in unlabelled grey west of Processing Rm',
 'CAV-S14-002': 'BF-5: leader ends off the plan',
 'VAV-B-S13-005': 'BF-5: two bars carry this tag and both walkers converge',
 'VAV-B-S10-001': 'BF-5: three walkers converge in the open purple',
 'VAV-B-S10-002': 'BF-5: leader ends in the grey Heritage Collection, not the purple',
 'VAV-B-S10-003': 'BF-5: leader ends in the grey Heritage Collection, not the purple',
 'VAV-B-S10-004': 'BF-5: leader ends in the grey Heritage Collection, not the purple',
 'VAV-B-S10-005': 'BF-5: two walkers converge',
 'VAV-B-S10-006': 'BF-5: leader not resolved',
 'VAV-B-S10-007': 'BF-5: two walkers converge',
 'VAV-B-S10-008': 'BF-5: two walkers converge',
 'VAV-B-S10-009': 'BF-5: two walkers converge in Instruction Presentation',
 'VAV-B-S10-015': 'BF-5: two walkers converge',
 'VAV-B-S10-018': 'BF-5: two walkers converge in Instruction Presentation',
 'CAV-S14-003': 'BF-6: leader ends on the Air Shaft row east of the plan',
 'CAV-S14-005': 'BF-6: five walkers converge below the plan',
 'CAV-S15-001': 'BF-6: leader ends on the Air Shaft row east of the plan',
 'VAV-B-S10-012': 'BF-6: five walkers converge below the plan',
 'VAV-B-S10-013': 'BF-6: five walkers converge below the plan',
 'VAV-B-S10-014': 'BF-6: five walkers converge below the plan',
 'VAV-B-S10-019': 'BF-6: five walkers converge below the plan',
 'VAV-B-S15-001': 'BF-7: leader not resolved',
 'VAV-B-S15-002': 'BF-7: four walkers converge below the plan',
 'VAV-B-S15-003': 'BF-7: four walkers converge below the plan',
 'VAV-B-S15-004': 'BF-7: leader not resolved',
 'VAV-B-S15-005': 'BF-7: leader not resolved',
 'VAV-B-S15-006': 'BF-7: four walkers converge below the plan',
 'VAV-B-S15-007': 'BF-7: leader ends in grey outside the purple',
 'VAV-B-S15-008': 'BF-7: leader not resolved',
 'VAV-B-S15-009': 'BF-7: leader ends in grey outside the purple',
 'VAV-B-S15-013': 'BF-7: dot is in the purple band but which side of the'
                  ' Prof. Librarian wall is not clear at any zoom',
 'FCU-B-029': 'BF-7: leader not resolved',
 'FCU-B-038': 'BF-7: four walkers converge below the plan',
 'VAV-B-S15-012': 'BF-8: leader ends outside the plan',
 'FCU-B-025': 'BF-10: leader not resolved',
 'CAV-S11-001': 'FF: leader not resolved',
 'CAV-S11-006': 'FF: dot sits on the west edge of Info. Literacy Instr.1 and'
                ' could be either side of the wall',
 'CAV-S11-007': 'FF: five walkers converge on one dot in Children Library',
 'CAV-S11-008': 'FF: five walkers converge on one dot in Children Library',
 'CAV-S11-009': 'FF: leader not resolved',
 'VAV-1F-S11-001': 'FF: leader not resolved',
 'VAV-1F-S11-007': 'FF: five walkers converge on one dot in Children Library',
 'VAV-1F-S11-008': 'FF: leader not resolved',
 'VAV-1F-S11-009': 'FF: five walkers converge on one dot in Children Library',
 'VAV-1F-S11-011': 'FF: leader not resolved',
 'VAV-1F-S11-012': 'FF: leader not resolved',
 'VAV-1F-S11-013': 'FF: two walkers converge',
 'VAV-1F-S11-014': 'FF: five walkers converge on one dot in Children Library',
 'VAV-1F-S11-017': 'FF: leader not resolved',
 'VAV-1F-S11-018': 'FF: five walkers converge on one dot in Children Library',
 'VAV-1F-S11-021': 'FF: two walkers converge',
 'VAV-1F-S11-089': 'FF: two walkers converge',
 'VAV-1F-S11-090': 'FF: two walkers converge',
 'VAV-1F-S15-005': 'FF: leader not resolved',
 'FCU-1F-002': 'FF: leader not resolved',
 'VAV-1F-S15-011': 'FF-2: leader not resolved',
 'CAV-S15-006': 'FF-2: leader ends outside the plan',
 'CAV-S15-018': 'FF-2: leader not resolved',
 'FCU-1F-059': 'FF-2: leader not resolved',
 'CAV-S15-010': 'FF-2: leader not resolved',
 'FCU-1F-062': 'FF-2: leader not resolved',
 'FCU-1F-063': 'FF-2: leader not resolved',
 'CAV-S15-014': 'FF-2: leader not resolved',
 'FCU-1F-004': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-005': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-006': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-007': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-008': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-009': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-010': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-011': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-012': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-013': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-014': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-015': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-016': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-017': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-018': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-019': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-021': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-022': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-023': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-024': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-025': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-026': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-027': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-028': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-029': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-030': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-031': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-032': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-033': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-034': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-035': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-036': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-037': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-038': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-039': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-040': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-041': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-042': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-043': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-044': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-045': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-046': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-047': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-048': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-049': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-050': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-051': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-052': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-053': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-054': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-055': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-057': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-058': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'FCU-1F-065': 'the screen names no room where this leader lands - column D calls it a bridge ceiling void, and the QNL screens do not label the voids',
 'VAV-2F-S12-001': 'SF-1: leader not resolved',
 'VAV-2F-S12-002': 'SF-1: leader not resolved',
 'VAV-2F-S12-004': 'SF-1: two walkers converge above the plan',
 'VAV-2F-S12-005': 'SF-1: two walkers converge above the plan',
 'VAV-2F-S12-015': 'SF-1: three walkers converge',
 'VAV-2F-S12-017': 'SF-1: leader not resolved',
 'VAV-2F-S12-018': 'SF-1: three walkers converge',
 'VAV-2F-S12-019': 'SF-1: three walkers converge',
 'VAV-2F-S12-020': 'SF-1: leader not resolved',
 'VAV-2F-S12-023': 'SF-1: three walkers converge east of the plan',
 'VAV-2F-S12-024': 'SF-1: leader ends above the plan',
 'VAV-2F-S12-025': 'SF-1: three walkers converge east of the plan',
 'VAV-2F-S12-027': 'SF-1: three walkers converge east of the plan',
 'VAV-2F-S12-028': 'SF-1: dot sits between Group Study Rm 7 and Rm 8',
 'VAV-2F-S12-097': 'SF-1: leader not resolved',
 'VAV-2F-S13-008 (SF-1)': 'SF-1: leader not resolved; read on SF-3 instead',
 'VAV-2F-S13-009': 'SF-1: leader not resolved',
 'VAV-2F-S13-011': 'SF-1: leader ends above the plan',
 'VAV-2F-S13-014': 'SF-1: leader not resolved',
 'VAV-2F-S10-006': 'SF-1: leader not resolved',
 'FCU-2F-005': 'SF-1: dot is in the grey south of Storage, which carries no label',
 'VAV-2F-S13-010': 'SF-3: dot is at the west edge of the yellow, on the wall',
 'VAV-2F-S13-015': 'SF-3: dot is in the yellow but not inside a labelled cell',
 'VAV-2F-S13-016': 'SF-3: leader not resolved',
 'VAV-2F-S13-002': "SF-3: dot is south of Lib. Director's Rm, in an unlabelled cell",
 'VAV-2F-S15-001': 'SF-3: leader ends above the plan',
 'VAV-2F-S15-003': 'SF-3: leader not resolved',
 'VAV-2F-S15-004': 'SF-3: leader not resolved',
 'VAV-2F-S14-001': 'SF-3: leader ends above the plan',
 'VAV-2F-S14-002': 'SF-3: leader not resolved',
 'VAV-2F-S14-003': 'SF-3: leader ends below the plan',
 'VAV-2F-S14-004': 'SF-3: leader ends below the plan',
 'VAV-2F-S14-016': 'SF-3: leader ends below the plan',
 'FCU-2F-037': 'SF-6: leader not resolved',
 'FCU-2F-038': 'SF-6: leader ends off the plan',
 'FCU-2F-039': 'SF-6: two walkers converge off the plan',
 'FCU-2F-040': 'SF-6: leader not resolved',
 'FCU-2F-048': 'SF-6: leader not resolved',
 'FCU-2F-053': 'SF-6: two walkers converge off the plan',
 'FCU-2F-003': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-004': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-056': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-057': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-058': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-059': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-060': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-061': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'FCU-2F-062': 'the screen names no room where this leader lands - the plan carries furniture and function labels (Book Shelf, Media Station, Special Events) but no room names',
 'SEF-RP0007': 'RF-2: all four fans land in the same unlabelled cell, which is at least consistent with all four sharing one plant zone - but the screen names no room, so nothing can be written',
 'SEF-RP0008': 'RF-2: all four fans land in the same unlabelled cell, which is at least consistent with all four sharing one plant zone - but the screen names no room, so nothing can be written',
 'SEF-RP0009': 'RF-2: all four fans land in the same unlabelled cell, which is at least consistent with all four sharing one plant zone - but the screen names no room, so nothing can be written',
 'EF-RP0002': 'RF-2: all four fans land in the same unlabelled cell, which is at least consistent with all four sharing one plant zone - but the screen names no room, so nothing can be written',
 'EF-RP0001': "RF-1: the roof plan carries no room label at all - only Zone 3 does - and three of the five icons on this screen carry the HMI default text 'Label' instead of a tag",
 'DX-B-05 (RF-1)': "RF-1: the roof plan carries no room label at all - only Zone 3 does - and three of the five icons on this screen carry the HMI default text 'Label' instead of a tag",
 'FCU-2F-001': 'Terrace Floor-2: the plan carries furniture and function labels (Computer Station, Media Station, Shell space) and no room names',
 'FCU-2F-002': 'Terrace Floor-2: the plan carries furniture and function labels (Computer Station, Media Station, Shell space) and no room names',
 'FCU-1F-001': 'Terrace Floor-2: the plan carries furniture and function labels (Computer Station, Media Station, Shell space) and no room names',
 'AHU-B0002': 'BF-2: leader ends off the plan',
 'AHU-B0013 (BF-2)': 'BF-2: leader not resolved',
 'EF-BBV0001': 'BF-2: leader not resolved',
 'EFT-B02': 'BF-2: the screen calls this icon EFT-B02 and the register has no such tag - the nearest are TEF_B02A and TEF_B02B, two rows for one icon, so which is meant cannot be decided',
 'AHU-B0001': 'BF-10: leader ends off the plan',
 'CAV-S14-001': 'BF-4: the dot this was traced to belongs to EF-B0007, whose own leader reaches it in a shorter walk and whose column D room (Loading Room B.109) is the area the dot sits in; CAV-S14-001 has no dot of its own once that is settled',
 'VAV-1F-S11-004': 'FF: S11-004 and S11-006 have one dot each in Info. Literacy Instr.1 and Instr.2, and the walker swaps which unit gets which depending on the order the dots are claimed in - the screen does not settle it',
 'VAV-1F-S11-006': 'FF: swaps with S11-004, see above',
 'DX-B0009': 'BF-5: the dot is in an unlabelled grey cell west of Security Store',
 'DX-B0002': 'BF-1: leader not resolved',
 'DX-B0007': 'BF-1: leader not resolved',
 'DX-B0008': 'BF-1: leader not resolved',
 'EF-B0005': 'BF-1: leader not resolved once DX-B0001 claims the dot',
 'EF-B0009': 'BF-1: leader not resolved',
 'AHU-B0013': 'BF-1, BF-2, BF-3 and SF-3 all draw this AHU and none of its leaders resolves to a dot',
 'AHU-B0014': 'BF-4, BF-6 and SF-3 draw it; the BF-6 leader lands in the plant area but not inside a labelled cell',
 'AHU-B0015': 'BF-4, BF-6, BF-8, FF and SF-3 draw it; no leader resolves into a labelled room',
 'AHU-B0004': 'BF-6: leader not resolved',
 'AHU-B0009': 'BF-6: leader not resolved',
 'TEF-B0001A': 'BF-6: the screen calls this TEF-B0001A and the register has TEF_B01A; the dot is in the cyan Plant Rm 3 / Corridor 5 space, which cannot be split',
 'EF-B0006': 'BF-4: leader not resolved',
 'EF-B0008': 'BF-4: leader not resolved once EF-B0007 claims its dot',
 'EF-B0015': 'BF-4: leader not resolved',
 'EF-B0016': 'BF-4: leader not resolved',
 'EF-B0010': 'BF-11: leader not resolved',
 'EF-B0011': 'BF-11: dot is east of the plan edge',
 'EF-B0012': 'BF-8: leader not resolved',
 'DX-B0005': 'BF-4: dot is in an unlabelled grey cell',
 'DX-B0013': 'BF-11: dot is east of the plan edge',
 'DX-B0015': 'BF-11: leader not resolved',
 'CCU-B001': 'BF-4: the dot is west of the Q-Tel Rm wall, in the unlabelled block with Dry store and BOH; column D says QTEL ROOM B.048',
 'CCU-B005': 'BF-3: leader not resolved',
 'CCU-B006': 'BF-3: dot is on the Storage / Security Equip. boundary',
 'CCU-B007': 'BF-3: leader not resolved',
 'CCU-8081': 'BF-4: leader not resolved',
 'CCU-8082': 'BF-4: leader not resolved',
 'CCU-8083': 'BF-4: leader not resolved',
 'CCU-8084': 'BF-4: leader not resolved',
 'CCU-B002': 'BF-4: leader not resolved',
 'CCU-B003': 'BF-4: leader not resolved',
 'CCU-B004': 'BF-4: leader not resolved',
 'EF-0201': 'FF and SF-3 both draw this fan and neither leader lands in a labelled room',
}

SCREEN_FILE = {k: 'QNL/%s.jpg' % k for k in SCREENS}

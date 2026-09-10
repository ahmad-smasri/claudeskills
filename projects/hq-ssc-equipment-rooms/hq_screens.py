"""What the HQ BMS screens say, for equipment other than AHU, VAV and FCU.

The HQ pass in `../bms-room-allocation` only ever read VAVs and FCUs, so these
were traced fresh off the screens with `annotate_all.py`. Each one was
confirmed by eye on the annotated image before being written down.

The HQ car park screens carry no room names at all - parking bay numbers,
`Exit`, `Public Vehicle Out` and nothing else - so the twenty-seven CEF fans
cannot be given a room from them however well their leaders resolve. They are
recorded here only as being on a named car park deck.
"""

# (tag, room, screen, confidence, note)
READ = [
    ('DX-B-0001', 'HV Room B.011', 'HQ/Basment Floor/BF-1', 'ok', ''),
    ('DX-B-0003', 'Unlabelled cell east of Transformer Substation B.010',
     'HQ/Basment Floor/BF-1', 'ok',
     'the top band of this plan is three cells and only the first two are'
     ' named; the dot is in the third'),
    ('DX-B-0011', 'UPS Room B.26', 'HQ/Basment Floor/BF-1', 'ok', ''),
    ('DX-B-0016', 'AHU - 3 B.022', 'HQ/Basment Floor/BF-2', 'ok', ''),
    ('CCU-B-0003A', 'Chauffer Room B.117', 'HQ/Basment Floor/BF-2', 'ok',
     'the dot is in the Chauffer Room band, one wall north of VIP Parking'
     ' B.106'),
    ('CCU-B-0005', 'VIP Parking B.115', 'HQ/Basment Floor/BF-2', 'check',
     'four leaders converge on one dot inside VIP Parking B.115, so the room'
     ' is certain and which of the four walked it is not'),
    ('CCU-B-0006', 'VIP Parking B.115', 'HQ/Basment Floor/BF-2', 'check',
     'four leaders converge on one dot inside VIP Parking B.115'),
    ('CCU-B-0007', 'VIP Parking B.115', 'HQ/Basment Floor/BF-2', 'check',
     'four leaders converge on one dot inside VIP Parking B.115'),
    ('CCU-B-0008', 'VIP Parking B.115', 'HQ/Basment Floor/BF-2', 'check',
     'four leaders converge on one dot inside VIP Parking B.115'),
]

# equipment drawn on the HQ screens that the ontology has no entity for at all
MISSING = [
    ('JF-B-0001', 'Jet fan', 'HQ/Cark Park/CPF-1'),
    ('JF-B-0002', 'Jet fan', 'HQ/Cark Park/CPF-1'),
    ('JF-B-0003', 'Jet fan', 'HQ/Cark Park/CPF-1'),
    ('JF-B-0004', 'Jet fan', 'HQ/Cark Park/CPF-1'),
    ('JF-B-0005', 'Jet fan', 'HQ/Cark Park/CPF-1'),
    ('JF-B-0006', 'Jet fan', 'HQ/Cark Park/CPF-1'),
    ('JF-B-0007', 'Jet fan', 'HQ/Cark Park/CPF-2'),
    ('JF-B-0008', 'Jet fan', 'HQ/Cark Park/CPF-2'),
    ('JF-B-0009', 'Jet fan', 'HQ/Cark Park/CPF-2'),
    ('JF-B-0010', 'Jet fan', 'HQ/Cark Park/CPF-2'),
    ('IF-B-0001', 'Induction fan', 'HQ/Cark Park/CPF-1'),
    ('IF-B-0002', 'Induction fan', 'HQ/Cark Park/CPF-1'),
    ('IF-B-0003', 'Induction fan', 'HQ/Cark Park/CPF-1'),
    ('IF-B-0004', 'Induction fan', 'HQ/Cark Park/CPF-2'),
    ('IF-B-0005', 'Induction fan', 'HQ/Cark Park/CPF-2'),
    ('IF-B-0006', 'Induction fan', 'HQ/Cark Park/CPF-2'),
    ('IF-B-0007', 'Induction fan', 'HQ/Cark Park/CPF-2'),
    ('IF-B-0008', 'Induction fan', 'HQ/Cark Park/CPF-2'),
]

# the screen each car park fan is drawn on - the decks carry no room names, so
# this is as far as the screens go for them
DECK = {}
for _n, _s in ((1, 'CPF-3'), (2, 'CPF-3'), (3, 'CPF-3'), (4, 'CPF-3'),
               (5, 'CPF-3'), (6, 'CPF-3'), (7, 'CPF-3'),
               (8, 'CPF-4'), (11, 'CPF-1'), (12, 'CPF-1'),
               (13, 'CPF-4'), (14, 'CPF-4'), (15, 'CPF-4'), (16, 'CPF-2'),
               (17, 'CPF-2'), (18, 'CPF-2'), (19, 'CPF-4'), (20, 'CPF-4'),
               (21, 'CPF-4'), (22, 'CPF-4'), (23, 'CPF-4'), (24, 'CPF-4'),
               (25, 'CPF-2'), (26, 'CPF-2'), (27, 'CPF-2')):
    DECK['B%02d' % _n] = 'HQ/Cark Park/%s' % _s

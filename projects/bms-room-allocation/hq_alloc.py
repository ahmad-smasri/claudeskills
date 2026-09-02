# HQ green-highlighted rows, read off the HQ BMS screens.
# On HQ screens the room name is set outside the room and joined to it by its
# own dashed pointer, so an equipment leader terminates at the room's NAME
# rather than inside the room polygon. SSC labelled rooms in place.
# (tag, room, screen, conf)
HQ = [
 ('VAV-0001', 'B.004 STAFF ENTRANCE',        'Basment Floor/BF-1', 'ok'),
 ('FCU-0005', 'B.401',                       'Basment Floor/BF-1', 'ok'),
 ('FCU-0097', 'B.512 IDF ROOM',              'Basment Floor/BF-2', 'ok'),
 ('FCU-0010', 'B.105',                       'Basment Floor/BF-2', 'check'),
 ('VAV-0595', 'B.116 LOBBY',                 'Basment Floor/BF-2', 'ok'),
 ('FCU-0017', 'G.005 CONTROL CENTER',        'Ground Floor/GF-1',  'ok'),
 ('VAV-0025', 'G.104 LOBBY',                 'Ground Floor/GF-1',  'ok'),
 ('VAV-0096', '1.101 STAFF LOUNGE',          '1F/FF-1',            'ok'),
 ('FCU-0114', '1.114 STAFF LOUNGE STORAGE',  '1F/FF-2',            'ok'),
 ('VAV-0102', '1.706 WASHING AREA',          '1F/FF-2',            'ok'),
 ('FCU-0064', '3.405 MALE TOILET',           '3F/3F-1',            'ok'),
 ('FCU-0065', '3.401 MALE TOILET',           '3F/3F-1',            'ok'),
 ('FCU-0066', '3.204 PANTRY',                '3F/3F-1',            'ok'),
 ('FCU-0074', '4.202 PRINT COPY',            '4F/4F-2',            'ok'),
 ('FCU-0075', '4.214 GSM ROOM',              '4F/4F-2',            'ok'),
 ('FCU-0076', '4.214 GSM ROOM',              '4F/4F-2',            'ok'),
 ('FCU-0132', 'SOUTH WEST CORRIDOR',         '9F/9F-1',            'ok'),
 ('FCU-0121', '11.110 ELECTRIC CLOSET',      '11F/11F-1',          'check'),
 ('VAV-0584', '11.208 SHEIKHA WING SHEIKHA ENSUIT', '11F/11F-2',   'ok'),
]

# The BMS leader ends in an area the screen does not name, so there is no room
# to write. Left blank rather than guessed.
HQ_UNNAMED = [
 ('FCU-0008', 'Basment Floor/BF-2', 'leader ends in an unlabelled room between B.107 and B.124'),
 ('FCU-0067', '3F/3F-2', 'leader ends in the unlabelled grey zone at the east edge'),
 ('FCU-0068', '3F/3F-2', 'leader ends in the unlabelled grey zone at the east edge'),
 ('FCU-0069', '3F/3F-2', 'leader ends in the unlabelled grey zone at the east edge'),
 ('FCU-0070', '3F/3F-2', 'leader ends in the unlabelled grey zone at the east edge'),
]

# SSC green rows that were still blank
SSC_EXTRA = [
 ('VAV-0102', '03.041', 'TF-part1', 'check'),
]
SSC_UNRESOLVED = [
 ('FCU-0009', 'FF-part2', 'leader could not be followed - runs along the plan border'),
 ('VAV-0038', 'FF-part1', 'no leader detected leaving the widget'),
]

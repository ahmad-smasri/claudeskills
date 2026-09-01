# HQ green-highlighted rows, read off the HQ BMS screens.
# NOTE on HQ screens: rooms are labelled with text placed outside the room and
# joined to it by its own dashed pointer, so an equipment leader terminates at
# the room's NAME, not inside the room polygon. SSC labelled rooms in place.
# (tag, room, screen, conf)
HQ = [
 ('VAV-0001', 'B.004 STAFF ENTRANCE',   'Basment Floor/BF-1', 'ok'),
 ('FCU-0005', 'B.401',                  'Basment Floor/BF-1', 'ok'),
 ('FCU-0097', 'B.512 IDF ROOM',         'Basment Floor/BF-2', 'ok'),
 ('FCU-0010', 'B.105',                  'Basment Floor/BF-2', 'check'),
 ('VAV-0595', 'B.116 LOBBY',            'Basment Floor/BF-2', 'ok'),
 ('FCU-0065', '3.401 MALE TOILET',      '3F/3F-1',            'ok'),
 ('FCU-0064', '3.405 MALE TOILET',      '3F/3F-1',            'ok'),
 ('FCU-0017', 'G.005 CONTROL CENTER',   'Ground Floor/GF-1',  'ok'),
 ('VAV-0025', 'G.104 LOBBY',            'Ground Floor/GF-1',  'ok'),
]
# still to read: FCU-0008, FCU-0066, FCU-0074, FCU-0075, FCU-0076, FCU-0114,
#                FCU-0121, FCU-0132, VAV-0096, VAV-0102, VAV-0584

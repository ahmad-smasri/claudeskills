# HQ 1F screen FF-1. Endpoints resolved by zone-then-label.
FF1 = [
 ('VAV-0082', 'VIP ENTRANCE (HIGH RISE)',   'FF-1', 'ok'),
 ('VAV-0081', 'VIP ENTRANCE (HIGH RISE)',   'FF-1', 'ok'),
 ('VAV-0080', 'VIP ENTRANCE (HIGH RISE)',   'FF-1', 'ok'),
 ('VAV-0079', '1.007 FINANCE STAFF',        'FF-1', 'ok'),
 ('VAV-0078', '1.006 FINANCE STAFF',        'FF-1', 'ok'),
 ('VAV-0077', '1.005 FINANCE SECRETARY',    'FF-1', 'ok'),
 # VAV-0076 endpoint sits on the 1.005/1.004 wall; D says 1.004. Not callable.
 ('VAV-0097', 'CORRIDOR',                   'FF-1', 'check'),
 ('VAV-0075', '1.003 MANAGER',              'FF-1', 'ok'),
 ('VAV-0074', '1.002 MANAGER',              'FF-1', 'ok'),
 # VAV-0091 ends in the big cyan zone by Stairs 4, which covers both the
 # staff lounge and the prayer room; D says 1.105. Not callable.
 ('VAV-0104', 'LOBBY (GROUND FLOOR)',       'FF-1', 'check'),
 ('VAV-0103', 'LOBBY (GROUND FLOOR)',       'FF-1', 'ok'),
 ('VAV-0087', '1.108 FINANCE MEETING ROOM', 'FF-1', 'check'),
 ('VAV-0088', '1.109 CONSULTANT SPACE',     'FF-1', 'ok'),
 # the screen labels this box 'Finance Room 1.106' and a separate box
 # 'Finance Cashier 1.116'; D says 1.116. Genuine disagreement, BMS wins.
 ('VAV-0093', '1.106 FINANCE ROOM',         'FF-1', 'ok'),
 ('VAV-0107', '1.701 STAFF CAFETERIA',      'FF-1', 'check'),
]

"""Basement and ground floor - the rows the first pass left blank, re-read
with the fixed detector.

Most of these were blank because the widget that owned the leader was never
found, not because the leader was unreadable. A few are still hard: the
three basement FCUs whose leaders come in from the right and stop on the
outer wall are called from the row they arrive on rather than from a dot
inside the room, and are flagged.
"""

BFGF = [
 # --- basement, BF-2 ---------------------------------------------------------
 ('FCU-0001', 'B.512 IDF ROOM',              'BF-2', 'check'),
 ('FCU-0003', 'B.107 DOCK MASTER OFFICE',    'BF-2', 'ok'),
 ('FCU-0006', 'B.122',                       'BF-2', 'check'),
 ('FCU-0007', 'B.123',                       'BF-2', 'check'),
 ('FCU-0008', 'B.014',                       'BF-2', 'check'),
 ('FCU-0009', 'B.014',                       'BF-2', 'check'),
 # FCU-0010 now traces to the B.105 band rather than B.124, but the row was
 # reviewed and cleared already, so it stays blank rather than being rewritten
 ('VAV-0006', 'B.116 LOBBY',                 'BF-2', 'check'),
 # FCU-0004 arrives on the outer wall with nothing to call it from - left blank

 # --- ground floor, GF-2 -----------------------------------------------------
 ('FCU-0111', 'G.512 IDF ROOM',              'GF-2', 'ok'),
 ('FCU-0014', 'G.512 IDF ROOM',              'GF-2', 'ok'),
 ('VAV-0053', 'G.108 CONSULTANT SPACE',      'GF-2', 'ok'),
 ('VAV-0039', 'G.030 PR & MARKET STAFF',     'GF-2', 'ok'),
 ('VAV-0040', 'G.029 PR & MARKET STAFF',     'GF-2', 'ok'),
 ('VAV-0043', 'G.026 FINANCE CASHIER',       'GF-2', 'ok'),
 ('VAV-0044', 'G.025 VIP LOUNGE',            'GF-2', 'ok'),
 ('VAV-0047', 'SOUTH EAST CORRIDOR',         'GF-2', 'ok'),
 ('FCU-0018', 'G.511 VESTIBULE',             'GF-2', 'ok'),
 ('VAV-0020', 'G.023 PR & MARKET STAFF',     'GF-2', 'ok'),

 # --- ground floor, GF-1 -----------------------------------------------------
 ('FCU-0016', 'G.017 COPY PRINT',            'GF-1', 'check'),
 ('VAV-0048', 'G.101 CONFERENCE ROOM',       'GF-1', 'check'),
 ('VAV-0049', 'G.101 CONFERENCE ROOM',       'GF-1', 'check'),
 ('FCU-0012', 'G.531 IDF ROOM',              'GF-1', 'check'),
]

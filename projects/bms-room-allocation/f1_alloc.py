"""First floor - screens FF-1 and FF-2, re-read with the fixed detector.

The finance block on FF-1 is the interesting part. The screen labels four
cells "Finance Cashier 1.116", "Finance Room 1.106", "Finance Auditor 1.117"
and "Finance Auditor 1.115"; the register pairs those names with different
numbers, and three of the four VAVs land in a different cell from the one
column D names.

This supersedes ff_alloc.py and ff2_alloc.py.
"""

F1 = [
 # --- FF-1, west --------------------------------------------------------------
 ('VAV-0081', '1.401 GROUND FLOOR VIP ENTRANCE', 'FF-1', 'ok'),
 ('VAV-0082', '1.401 GROUND FLOOR VIP ENTRANCE', 'FF-1', 'ok'),
 ('VAV-0080', '1.401 GROUND FLOOR VIP ENTRANCE', 'FF-1', 'ok'),
 ('VAV-0079', '1.007 FINANCE STAFF',           'FF-1', 'ok'),
 ('VAV-0078', '1.006 FINANCE STAFF',           'FF-1', 'ok'),
 ('VAV-0077', '1.005 FINANCE SECRETARY',       'FF-1', 'ok'),
 ('VAV-0076', '1.004 FINANCE MANAGER',         'FF-1', 'ok'),
 ('VAV-0075', '1.003 FINANCE MANAGER',         'FF-1', 'ok'),
 ('VAV-0074', '1.002 FINANCE MANAGER',         'FF-1', 'ok'),
 ('VAV-0073', '1.001 FINANCE SECRETARY',       'FF-1', 'ok'),
 ('VAV-0107', '1.701 STAFF CAFETERIA',         'FF-1', 'ok'),
 ('VAV-0096', '1.101 STAFF LOUNGE',            'FF-1', 'ok'),
 ('VAV-0097', '1.602 CORRIDOR',                'FF-1', 'ok'),
 ('VAV-0091', '1.105 PRAYER ROOM',             'FF-1', 'check'),
 ('VAV-0071', '1.028 FINANCE MANAGER',         'FF-1', 'ok'),
 ('VAV-0083', '1.101 STAFF LOUNGE',            'FF-1', 'ok'),
 ('FCU-0019', '1.531 IDF ROOM',                'FF-1', 'ok'),
 ('VAV-0084', '1.101 STAFF LOUNGE',            'FF-1', 'ok'),
 ('FCU-0020', '1.531 IDF ROOM',                'FF-1', 'ok'),
 ('VAV-0085', '1.101 STAFF LOUNGE',            'FF-1', 'ok'),
 ('VAV-0101', '1.702 FOOD HEAT UP',            'FF-1', 'ok'),
 ('VAV-0072', '1.029 FINANCE MANAGER',         'FF-1', 'ok'),
 ('VAV-0070', '1.027 FINANCE MANAGER',         'FF-1', 'ok'),
 ('VAV-0069', '1.026 FINANCE STAFF',           'FF-1', 'ok'),
 ('VAV-0068', '1.025 FINANCE STAFF',           'FF-1', 'ok'),
 ('VAV-0067', '1.024 FINANCE AUDIT',           'FF-1', 'ok'),
 ('VAV-0104', 'LOBBY (GROUND FLOOR)',          'FF-1', 'ok'),
 ('VAV-0103', 'LOBBY (GROUND FLOOR)',          'FF-1', 'ok'),
 ('VAV-0088', '1.109 CONSULTANT SPACE',        'FF-1', 'ok'),
 ('VAV-0092', '1.117 FINANCE AUDITOR',         'FF-1', 'check'),
 ('VAV-0095', '1.115 FINANCE AUDITOR',         'FF-1', 'ok'),
 ('VAV-0065', '1.022 FINANCE SEC',             'FF-1', 'ok'),
 ('VAV-0086', '1.101 STAFF LOUNGE',            'FF-1', 'ok'),
 ('VAV-0087', '1.108 FINANCE MEETING ROOM',    'FF-1', 'ok'),
 ('VAV-0094', '1.116 FINANCE CASHIER',         'FF-1', 'check'),
 ('VAV-0093', '1.106 FINANCE ROOM',            'FF-1', 'check'),
 ('VAV-0066', '1.023 FINANCE AUDIT',           'FF-1', 'ok'),

 # --- FF-2, east --------------------------------------------------------------
 ('VAV-0108', '1.701 STAFF CAFETERIA',         'FF-2', 'ok'),
 ('VAV-0106', 'LOBBY (GROUND FLOOR)',          'FF-2', 'ok'),
 ('VAV-0105', 'LOBBY (GROUND FLOOR)',          'FF-2', 'ok'),
 # the leader ends in the lobby, not in the conference room column D names
 ('VAV-0090', 'LOBBY (GROUND FLOOR)',          'FF-2', 'check'),
 ('VAV-0089', '1.109 CONSULTANT SPACE',        'FF-2', 'ok'),
 ('VAV-0098', '1.602 CORRIDOR',                'FF-2', 'ok'),
 ('FCU-0021', '1.512 IDF ROOM',                'FF-2', 'ok'),
 ('FCU-0114', '1.114 STAFF LOUNGE STORAGE',    'FF-2', 'ok'),
 ('FCU-0022', '1.112 PRINT COPY',              'FF-2', 'ok'),
 ('VAV-0064', '1.021 FINANCE SEC',             'FF-2', 'ok'),
 ('VAV-0063', '1.020 FINANCE MANAGER',         'FF-2', 'ok'),
 ('VAV-0100', '1.111 FINANCE RECORD STORAGE',  'FF-2', 'ok'),
 ('VAV-0062', '1.019 FINANCE MANAGER',         'FF-2', 'ok'),
 ('VAV-0099', 'SOUTH EAST ZONE',               'FF-2', 'ok'),
 ('VAV-0102', '1.706 WASHING AREA',            'FF-2', 'ok'),
 ('VAV-0054', '1.011 FINANCE MANAGER',         'FF-2', 'ok'),
 ('VAV-0055', '1.012 FINANCE MANAGER',         'FF-2', 'ok'),
 ('VAV-0056', '1.013 FINANCE MANAGER',         'FF-2', 'ok'),
 ('VAV-0057', '1.014 FINANCE STAFF',           'FF-2', 'ok'),
 ('VAV-0058', '1.015 FINANCE STAFF',           'FF-2', 'ok'),
 ('VAV-0059', '1.016 FINANCE SECRETARY',       'FF-2', 'ok'),
 ('VAV-0060', '1.017 FINANCE DIRECTOR',        'FF-2', 'ok'),
 ('VAV-0061', '1.018 FINANCE MANAGER',         'FF-2', 'ok'),
]

"""Third floor - screens 3F-1 and 3F-2.

Read with the v6 tracer, which finds every slider on the screen (the earlier
one missed any bar whose position tick was two pixels wide or was crossed by a
leader).  Forty-four of the forty-five units on 3F-1 and all thirty-two on
3F-2 land in the room column D already names, so this floor is a calibration
run as much as a reading.
"""

F3 = [
 # --- 3F-1, the north-west screen -------------------------------------------
 ('VAV-0157', '3.017 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0189', '3.016 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0187', '3.014 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0186', '3.013 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0198', '3.011 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0196', '3.009 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0194', '3.007 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0192', '3.005 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0201', 'SOUTH WEST CORRIDOR',             '3F-1', 'ok'),
 ('VAV-0180', '3.001 LOUNGE',                    '3F-1', 'ok'),
 ('VAV-0185', '3.012 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0159', '3.019 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('FCU-0059', '3.531 IDF ROOM',                  '3F-1', 'ok'),
 ('VAV-0188', '3.015 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0197', '3.010 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0195', '3.008 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0193', '3.006 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0191', '3.004 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0190', '3.003 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0158', '3.018 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0200', '3.002 HR IMMIG STAFF',            '3F-1', 'ok'),
 # the screen drops FCU-0060 into the corridor cell east of 3.531, not into
 # the IDF room itself, where D and the FCU list both put it
 ('FCU-0060', 'NORTH WEST CORRIDOR',             '3F-1', 'check'),
 ('VAV-0160', '3.020 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0199', '3.101 OFFICE SPACE',              '3F-1', 'ok'),
 ('VAV-0161', '3.021 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0162', '3.022 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0164', '3.024 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0165', '3.025 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0166', '3.026 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0163', '3.023 HR IMMIG STAFF',            '3F-1', 'ok'),
 ('VAV-0178', '3.105A FEMALE PRAYER ROOM',       '3F-1', 'ok'),
 ('VAV-0177', '3.36 ABLUTION ROOM',              '3F-1', 'ok'),
 ('VAV-0202', '3.202A OFFICE SPACE',             '3F-1', 'ok'),
 # these three sit in the open bridge zone, which is what D calls them; the
 # value delivered earlier (a toilet, a pantry) was a mis-read and is corrected
 ('FCU-0065', '3.63 CORRIDOR BRIDGE',            '3F-1', 'ok'),
 ('VAV-0184', '3.104 HR IMMG SECRETARY',         '3F-1', 'ok'),
 ('VAV-0204', '3.205 HR IMMIGRATION',            '3F-1', 'ok'),
 ('FCU-0066', '3.63 CORRIDOR BRIDGE',            '3F-1', 'ok'),
 ('FCU-0062', '3.203 COPY/PRINT',                '3F-1', 'ok'),
 ('VAV-0217', '3.201 PROC. & CONTR. DIR. E',     '3F-1', 'ok'),
 ('FCU-0063', '3.103 PRINT COPY',                '3F-1', 'ok'),
 ('VAV-0181', '3.102 CONSULTANT SPACE TRAINEES', '3F-1', 'ok'),
 ('VAV-0183', '3.102 CONSULTANT SPACE TRAINEES', '3F-1', 'ok'),
 ('FCU-0064', '3.63 CORRIDOR BRIDGE',            '3F-1', 'ok'),
 ('VAV-0203', '3.202B OFFICE SPACE',             '3F-1', 'ok'),
 ('VAV-0182', '3.102 CONSULTANT SPACE TRAINEES', '3F-1', 'ok'),

 # --- 3F-2, the north-east screen -------------------------------------------
 ('VAV-0208', '3.209 HR IMMIG MANAGER',          '3F-2', 'ok'),
 ('VAV-0207', '3.208 HR IMMIG MANAGER',          '3F-2', 'ok'),
 ('VAV-0176', 'NORTH EAST CORRIDOR',             '3F-2', 'ok'),
 ('VAV-0175', '3.105B OFFICE SPACE',             '3F-2', 'ok'),
 ('VAV-0206', '3.207 HR IMMIG MANAGER',          '3F-2', 'ok'),
 ('VAV-0205', '3.206 HR IMMIG MANAGER',          '3F-2', 'ok'),
 ('VAV-0221', '3.602 SOUTH EAST CORRIDOR',       '3F-2', 'ok'),
 ('VAV-0220', '3.302 HR IMMG. MEETING ROOM',     '3F-2', 'ok'),
 ('VAV-0218', '3.301 PROC. & CONTR. MEETING ROOM', '3F-2', 'ok'),
 ('VAV-0216', '3.216 PROC. CONTR. SECRETARY',    '3F-2', 'ok'),
 ('VAV-0167', '3.027 HR IMMIG STAFF',            '3F-2', 'ok'),
 ('VAV-0168', '3.028 HR IMMIG STAFF',            '3F-2', 'ok'),
 ('FCU-0061', '3.512 IDF ROOM',                  '3F-2', 'ok'),
 ('VAV-0169', '3.029 HR IMMIG STAFF',            '3F-2', 'ok'),
 ('VAV-0170', '3.030 HR IMMIG STAFF',            '3F-2', 'ok'),
 ('VAV-0171', '3.031 HR IMMIG STAFF',            '3F-2', 'ok'),
 ('VAV-0179', 'NORTH EAST CORRIDOR',             '3F-2', 'ok'),
 ('VAV-0172', '3.032 HR IMMIG STAFF',            '3F-2', 'ok'),
 ('VAV-0214', '3.214 IT DIR. ENSUIT',            '3F-2', 'ok'),
 ('VAV-0215', '3.215 IT DIR. ENSUIT',            '3F-2', 'ok'),
 ('VAV-0174', '3.033 MEETING ROOM',              '3F-2', 'ok'),
 ('VAV-0213', '3.213 HR IMMIG DIR. ENSUIT',      '3F-2', 'ok'),
 ('VAV-0209', '3.210 HR IMMIG OFFICER',          '3F-2', 'ok'),
 ('VAV-0210', '3.210 HR IMMIG OFFICER',          '3F-2', 'ok'),
 ('VAV-0211', '3.211 HR IMMIG MANAGER',          '3F-2', 'ok'),
 ('VAV-0212', '3.212 HR IMMIG SEC.',             '3F-2', 'ok'),
 ('VAV-0219', '3.301 PROC. & CONTR. MEETING ROOM', '3F-2', 'ok'),
 ('VAV-0173', '3.033 MEETING ROOM',              '3F-2', 'ok'),
 # FCU-0067 to FCU-0070 end in the unshaded bridge strip between the north
 # east zone and the south east zone; the screen prints no room there, so
 # nothing is written - D says 'north east zone', the FCU list 'bridge BR-3'
 ('FCU-0067', '', '3F-2', 'unlabelled'),
 ('FCU-0068', '', '3F-2', 'unlabelled'),
 ('FCU-0069', '', '3F-2', 'unlabelled'),
 ('FCU-0070', '', '3F-2', 'unlabelled'),
]

"""Fourth floor - screens 4F-1 and 4F-2.

Two real disagreements with the register on this floor:
  * VAV-0233 and VAV-0234 are swapped - the screen puts VAV-0233 in 4.015A
    and VAV-0234 in 4.015C, the register the other way round.
  * FCU-0071 and FCU-0072 are filed as IDF Room 4.531, but nothing on 4F-1
    points at 4.531; both leaders end at the north-east corner, FCU-0072 in
    the pantry cell and FCU-0071 in the corridor band above it.
"""

F4 = [
 # --- 4F-1 -------------------------------------------------------------------
 ('VAV-0222', '4.004 STR. PL. DIR. ENSUIT',   '4F-1', 'ok'),
 ('VAV-0243', '4.003 SECRETARY',              '4F-1', 'ok'),
 ('VAV-0242', '4.002 MANAGER',                '4F-1', 'ok'),
 ('FCU-0083', '4.702 TERRACE',                '4F-1', 'ok'),
 ('FCU-0082', '4.703 TERRACE',                '4F-1', 'ok'),
 ('FCU-0081', '4.702 TERRACE',                '4F-1', 'ok'),
 ('VAV-0600', '4.001H OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0247', '4.001G OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0246', '4.001F OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0598', '4.001E OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0245', '4.001D OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0599', '4.001C OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0244', '4.001B OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0223', '4.005 STR.PL.DIR.MEETING ROOM','4F-1', 'ok'),
 ('VAV-0224', '4.006 STR. PL. DIR. MANAGER',  '4F-1', 'ok'),
 ('VAV-0225', '4.007 STR. PL. DIR. MANAGER',  '4F-1', 'ok'),
 ('VAV-0226', '4.008 STR. PL. DIR. MANAGER',  '4F-1', 'ok'),
 # the leader turns down into the unnamed corridor cell east of the pantry
 ('FCU-0071', '',                             '4F-1', 'unlabelled'),
 ('VAV-0239', '4.107 STR. PL. DIR. TECH. STAFF', '4F-1', 'ok'),
 ('VAV-0241', '4.104 WAITING LOUNGE',         '4F-1', 'ok'),
 ('VAV-0248', '4.103 STORAGE SPACE',          '4F-1', 'ok'),
 # FCU-0077 to FCU-0080 end in the open part of the south-west floorplate,
 # which 4F-1 does not name; the register calls them VP Adm Terrace 4.701
 ('FCU-0080', '',                             '4F-1', 'unlabelled'),
 ('VAV-0251', 'SOUTH WEST CORRIDOR',          '4F-1', 'ok'),
 ('FCU-0078', '',                             '4F-1', 'unlabelled'),
 ('VAV-0597', '4.001A OFFICE SPACE',          '4F-1', 'ok'),
 ('VAV-0227', '4.009 STR. PL. DIR. HEAD OF PL.', '4F-1', 'ok'),
 ('FCU-0072', '4.105 PANTRY',                 '4F-1', 'check'),
 ('VAV-0238', '4.108 STR. PL. DIR. TECH. STAFF', '4F-1', 'ok'),
 ('VAV-0240', '4.104 WAITING LOUNGE',         '4F-1', 'ok'),
 ('VAV-0249', '4.102 OFFICE SPACE',           '4F-1', 'ok'),
 ('VAV-0250', '4.101 OFFICE SPACE',           '4F-1', 'ok'),
 ('FCU-0077', '',                             '4F-1', 'unlabelled'),
 ('FCU-0079', '',                             '4F-1', 'unlabelled'),

 # --- 4F-2 -------------------------------------------------------------------
 ('VAV-0228', '4.010 STR. PL. DIR. HEAD OF PL.', '4F-2', 'ok'),
 ('VAV-0237', 'NORTH EAST CORRIDOR',          '4F-2', 'ok'),
 ('VAV-0236', '4.109 VP EDU STORAGE',         '4F-2', 'ok'),
 ('VAV-0255', '4.206 VP ADM MANAGER',         '4F-2', 'ok'),
 ('VAV-0254', '4.205 VP ADM MANAGER',         '4F-2', 'ok'),
 ('VAV-0253', '4.204 OFFICE SPACE',           '4F-2', 'ok'),
 ('FCU-0073', '4.512 IDF ROOM',               '4F-2', 'ok'),
 ('FCU-0074', '4.202 PRINT COPY',             '4F-2', 'ok'),
 ('FCU-0076', '4.214 GSM ROOM',               '4F-2', 'ok'),
 ('FCU-0075', '4.214 GSM ROOM',               '4F-2', 'ok'),
 ('VAV-0252', '4.201 OFFICE SPACE',           '4F-2', 'ok'),
 ('VAV-0264', '4.301 VP ADM MEETING ROOM',    '4F-2', 'ok'),
 ('VAV-0229', '4.011 STR. PL. DIR. HEAD OF PL.', '4F-2', 'ok'),
 ('VAV-0230', '4.012 STR. PL. DIR. HEAD OF PL.', '4F-2', 'ok'),
 ('VAV-0231', '4.013 STR. PL. DIR. HEAD OF PL.', '4F-2', 'ok'),
 ('VAV-0232', '4.014 STR. PL. DIR. MANAGER',  '4F-2', 'ok'),
 ('VAV-0233', '4.015A OFFICE SPACE',          '4F-2', 'check'),
 ('VAV-0596', '4.015B OFFICE SPACE',          '4F-2', 'ok'),
 ('VAV-0234', '4.015C OFFICE SPACE',          '4F-2', 'check'),
 ('VAV-0235', 'NORTH EAST CORRIDOR',          '4F-2', 'ok'),
 ('FCU-0084', '4.110 PRINT COPY',             '4F-2', 'ok'),
 ('VAV-0257', '4.208 VP ADM SEC.',            '4F-2', 'ok'),
 ('VAV-0256', '4.208 VP ADM SEC.',            '4F-2', 'ok'),
 ('VAV-0258', '4.209 VP ADM MANAGER',         '4F-2', 'ok'),
 ('VAV-0265', 'SOUTH EAST CORRIDOR',          '4F-2', 'ok'),
 ('VAV-0259', '4.210 MANAGER',                '4F-2', 'ok'),
 ('VAV-0260', '4.211 VP ADMIN',               '4F-2', 'ok'),
 ('VAV-0261', '4.212 VP ADM PERS. ASS.',      '4F-2', 'ok'),
 ('VAV-0263', '4.301 VP ADM MEETING ROOM',    '4F-2', 'ok'),
 ('VAV-0262', '4.213 VP ADM ENSUIT',          '4F-2', 'ok'),
 ('VAV-0266', 'SOUTH EAST CORRIDOR',          '4F-2', 'ok'),
]

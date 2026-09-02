"""Eighth and ninth floors.

8F is one screen and reads cleanly. On 9F the two IDF FCUs behave the way
they have on every floor above the third: FCU-0112 sits in the IDF room,
FCU-0110 does not - its leader ends in the 9.532 cell next door, while the
register files it as IDF Room 9.531.
"""

F8 = [
 ('VAV-0433', '8.001 OBSERVATION SPACE',      '8F', 'ok'),
 ('VAV-0437', '8.001 OBSERVATION SPACE',      '8F', 'ok'),
 ('VAV-0436', '8.001 OBSERVATION SPACE',      '8F', 'ok'),
 ('VAV-0434', '8.001 OBSERVATION SPACE',      '8F', 'ok'),
 ('VAV-0435', '8.001 OBSERVATION SPACE',      '8F', 'ok'),
 ('VAV-0594', 'VISITORS CENTER',              '8F', 'ok'),
 ('VAV-0593', 'VISITORS CENTER',              '8F', 'ok'),
 ('VAV-0592', 'VISITORS CENTER',              '8F', 'ok'),
 ('VAV-0443', '8.602 VISITORS CENTER CORRIDOR','8F', 'ok'),
 ('FCU-0109', '8.512 IDF ROOM',               '8F', 'ok'),
 ('VAV-0442', '8.602 VISITORS CENTER CORRIDOR','8F', 'ok'),
 ('VAV-0438', '8.002 VISITORS CENTER OFFICE', '8F', 'ok'),
 ('VAV-0439', '8.602 VISITORS CENTER CORRIDOR','8F', 'ok'),
 ('VAV-0440', '8.602 VISITORS CENTER CORRIDOR','8F', 'ok'),
 ('VAV-0441', '8.602 VISITORS CENTER CORRIDOR','8F', 'ok'),
]

F9 = [
 # --- 9F-1 -------------------------------------------------------------------
 # the leader ends in the 9.532 cell east of the IDF room, not in 9.531
 ('FCU-0110', '9.532',                        '9F-1', 'check'),
 ('VAV-0486', '9.008 LEGAL SUP. SEC.',        '9F-1', 'ok'),
 ('VAV-0484', '9.006 LEGAL CONSULE',          '9F-1', 'ok'),
 ('VAV-0478', 'SOUTH WEST CORRIDOR',          '9F-1', 'ok'),
 ('VAV-0481', '9.003 LEGAL CONSULE',          '9F-1', 'ok'),
 ('FCU-0132', '9.101 VISITOR CENTER',         '9F-1', 'check'),
 ('VAV-0477', '9.041 BMO ARCHIVE ROOM',       '9F-1', 'ok'),
 ('VAV-0488', '9.010 LEGAL ADV. ENSUIT',      '9F-1', 'ok'),
 ('VAV-0487', '9.009 LEGAL SUP. SEC.',        '9F-1', 'ok'),
 ('VAV-0485', '9.007 LEGAL CONSULE',          '9F-1', 'ok'),
 ('VAV-0483', '9.005 LEGAL CONSULE',          '9F-1', 'ok'),
 ('VAV-0482', '9.004 LEGAL CONSULE',          '9F-1', 'ok'),
 ('VAV-0480', '9.002 LEGAL CONSULE',          '9F-1', 'ok'),
 ('VAV-0479', '9.001 LEGAL ARCHIVE',          '9F-1', 'ok'),
 ('VAV-0444', '9.011 BMO EXEC. ASSIST.',      '9F-1', 'ok'),
 ('VAV-0445', '9.012 BMO EXEC. ASSIST.',      '9F-1', 'ok'),
 ('VAV-0446', '9.013 BMO EXEC. ASSIST.',      '9F-1', 'ok'),
 ('VAV-0447', '9.014 BMO EXEC. ASSIST.',      '9F-1', 'ok'),
 ('VAV-0448', '9.015 BMO EXEC. ASSIST.',      '9F-1', 'ok'),
 ('VAV-0449', '9.016 BMO EXEC. ASSIST.',      '9F-1', 'ok'),
 ('VAV-0476', '9.040 BMO SAFE',               '9F-1', 'ok'),
 ('VAV-0475', '9.039 MEETING ROOM',           '9F-1', 'ok'),
 ('VAV-0474', 'HH-WING CORRIDOR 9.601',       '9F-1', 'ok'),
 # ends in the waiting area, not in the toilet block printed inside it
 ('VAV-0491', '9.104 BMO WAITING AREA',       '9F-1', 'check'),
 ('VAV-0490', '9.104 BMO WAITING AREA',       '9F-1', 'ok'),
 ('VAV-0489', '9.105 LOUNGE',                 '9F-1', 'ok'),
 ('VAV-0473', 'SOUTH WEST CORRIDOR',          '9F-1', 'ok'),
 ('VAV-0472', '9.038 BOD EXECUTIVE',          '9F-1', 'ok'),

 # --- 9F-2 -------------------------------------------------------------------
 ('VAV-0450', '9.017 BMO EXEC. ASSIST.',      '9F-2', 'ok'),
 ('VAV-0492', 'NORTH EAST CORRIDOR',          '9F-2', 'ok'),
 # ends in the unnamed purple cell west of the kitchen, not in the dining area
 ('VAV-0497', '',                             '9F-2', 'unlabelled'),
 ('VAV-0496', '9.108 KITCHEN',                '9F-2', 'ok'),
 ('VAV-0495', 'SOUTH EAST CORRIDOR',          '9F-2', 'ok'),
 ('FCU-0112', '9.512 IDF ROOM',               '9F-2', 'ok'),
 ('VAV-0471', '9.037 BOD SEC.',               '9F-2', 'ok'),
 ('VAV-0451', '9.018 BMO EXEC. SEC.',         '9F-2', 'ok'),
 ('VAV-0452', '9.019 BMO EXEC. SEC.',         '9F-2', 'ok'),
 ('VAV-0453', '9.020 BMO EXEC. SEC.',         '9F-2', 'ok'),
 ('VAV-0493', '9.110 SHEIKA WING DINING AREA','9F-2', 'ok'),
 ('VAV-0454', '9.021 BMO OPER. DIR. ENSUIT',  '9F-2', 'ok'),
 ('VAV-0470', '9.036 BOD EXECUTIVE',          '9F-2', 'ok'),
 ('VAV-0469', '9.035 HR EDU. ADV. ENSUIT',    '9F-2', 'ok'),
 ('VAV-0468', '9.034 HR EDU. ADV. ENSUIT',    '9F-2', 'ok'),
 ('VAV-0494', '9.110 SHEIKA WING DINING AREA','9F-2', 'ok'),
 ('VAV-0455', '9.022 BMO EXEC. ASSIST.',      '9F-2', 'ok'),
 ('VAV-0456', '9.023 BMO EXEC. SEC.',         '9F-2', 'ok'),
 ('VAV-0457', '9.024 BMO EXEC. SEC.',         '9F-2', 'ok'),
 ('VAV-0458', '9.025 BMO EXEC. SEC.',         '9F-2', 'ok'),
 ('VAV-0459', '9.025 BMO EXEC. SEC.',         '9F-2', 'ok'),
 ('VAV-0460', '9.026 BMO SUPP. SEC.',         '9F-2', 'ok'),
 ('VAV-0461', '9.027 BMO SUPP. SEC.',         '9F-2', 'ok'),
 ('VAV-0462', '9.028 BMO SUPP. SEC.',         '9F-2', 'ok'),
 ('VAV-0463', '9.029 BMO SUPP. SEC.',         '9F-2', 'ok'),
 ('VAV-0464', '9.030 BMO SUPP. SEC.',         '9F-2', 'ok'),
 ('VAV-0465', '9.031 BMO PRINT COPY',         '9F-2', 'ok'),
 ('VAV-0466', '9.032 BMO STORAGE',            '9F-2', 'ok'),
 ('VAV-0467', '9.033 HR EDU. ADV. ENSUIT',    '9F-2', 'ok'),
]

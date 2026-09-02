"""Tenth and eleventh floors and the roof.

Three findings on these floors:

  * 10.002B/C/D. The five shell-space VAVs run down the west wall in order,
    and the screen reads E, D, C, B, A from the top. The register has the
    middle three shifted - and the letters in the FCU/VAV list (column H)
    agree with the screen, not with the numbers in column D.
  * FCU-0122 and FCU-0123 (11F) are swapped: the screen puts FCU-0122 in the
    print copy room 11.108 and FCU-0123 in the MCC/electrical room 11.106.
  * The Sheikha ensuit on 11F is drawn as 11.208, which is what the FCU/VAV
    list calls it; column D says 11.202.

The roof screens repeat the level 11 VAVs and the level 8 visitor centre
VAVs; those readings are taken from the floor screen, not from the roof.
"""

F10 = [
 # --- 10F-1 ------------------------------------------------------------------
 ('VAV-0499', '10.006 EXEC. DIR. ARCH. COORD',  '10F-1', 'ok'),
 ('VAV-0535', '10.004 ARCHIVE COORD',           '10F-1', 'ok'),
 ('VAV-0533', '10.003 BOARD ROOM WAITING',      '10F-1', 'ok'),
 ('VAV-0548', '10.002E OFFICE SPACE',           '10F-1', 'ok'),
 ('VAV-0549', '10.002C OFFICE SPACE',           '10F-1', 'check'),
 ('VAV-0551', '10.002A OFFICE SPACE',           '10F-1', 'ok'),
 ('VAV-0532', '10.001 SHEIKHA WING STORAGE',    '10F-1', 'ok'),
 ('VAV-0530', '10.001 SHEIKHA WING STORAGE',    '10F-1', 'ok'),
 ('VAV-0500', '10.007 EXEC. DIR. PROT. ASSIS.', '10F-1', 'ok'),
 ('VAV-0534', '10.003 BOARD ROOM WAITING',      '10F-1', 'ok'),
 ('VAV-0536', '10.106 LOUNGE',                  '10F-1', 'ok'),
 ('VAV-0601', '10.002D OFFICE SPACE',           '10F-1', 'check'),
 ('VAV-0550', '10.002B OFFICE SPACE',           '10F-1', 'check'),
 ('VAV-0546', 'HH-WING CORRIDOR 10.601',        '10F-1', 'ok'),
 ('VAV-0531', '10.001 SHEIKHA WING STORAGE',    '10F-1', 'ok'),
 ('FCU-0116', '10.038 PRINT COPY',              '10F-1', 'ok'),
 ('VAV-0498', '10.005 ARCHIVE',                 '10F-1', 'ok'),
 ('FCU-0113', '10.531 IDF ROOM',                '10F-1', 'ok'),
 ('VAV-0501', '10.008 SCHED OFFICER',           '10F-1', 'ok'),
 ('VAV-0502', '10.009 CEREM. OFFICER',          '10F-1', 'ok'),
 ('VAV-0503', '10.010 CEREM. OFFICER',          '10F-1', 'ok'),
 ('VAV-0504', '10.011 CEREM. OFFICER',          '10F-1', 'ok'),
 ('VAV-0506', '10.013 TR. & VIS. OFFICER',      '10F-1', 'ok'),
 ('FCU-0117', '10.014 PRINT COPY',              '10F-1', 'ok'),
 ('VAV-0529', '10.037 SH. SERV. DIR. SR. ACCOUNT.', '10F-1', 'ok'),
 ('VAV-0528', '10.036 SH. SERV. DIR. ACCOUNT.', '10F-1', 'ok'),
 ('VAV-0527', '10.035 SUPP. OFFICER',           '10F-1', 'ok'),
 ('VAV-0526', '10.034 COMM. DIR. COORD',        '10F-1', 'ok'),
 ('VAV-0505', '10.012 TR. & VIS. OFFICER',      '10F-1', 'ok'),
 ('VAV-0538', '10.109 BOARD PREP. ROOM',        '10F-1', 'ok'),
 ('VAV-0543', 'HH-WING CORRIDOR 10.601',        '10F-1', 'ok'),
 ('VAV-0537', '10.106 NW LOUNGE',               '10F-1', 'ok'),
 ('VAV-0544', 'HH-WING CORRIDOR 10.601',        '10F-1', 'ok'),
 # the screen calls this room 10.002; the register says 10.102
 ('VAV-0547', '10.002 SHEIKHA WING MULTI PURPOSE ROOM', '10F-1', 'check'),
 ('VAV-0522', 'HH-WING CORRIDOR 10.601',        '10F-1', 'ok'),
 ('VAV-0525', '10.033 COMM. DIR. TRANSLTOR',    '10F-1', 'ok'),

 # --- 10F-2 ------------------------------------------------------------------
 ('VAV-0507', '10.015 SCHED OFFICER',           '10F-2', 'ok'),
 ('VAV-0508', '10.016 PLANNING ANALYST',        '10F-2', 'ok'),
 ('VAV-0509', '10.017 STRAT. PLANNER',          '10F-2', 'ok'),
 ('VAV-0545', 'NORTH EAST CORRIDOR',            '10F-2', 'ok'),
 ('VAV-0542', 'NORTH EAST CORRIDOR',            '10F-2', 'ok'),
 # both of these end in the AV room 10.112; D files FCU-0118 as 10.111
 ('FCU-0118', '10.112 AV ROOM',                 '10F-2', 'check'),
 ('VAV-0541', '10.112 AV ROOM',                 '10F-2', 'ok'),
 ('FCU-0115', '10.512 IDF ROOM',                '10F-2', 'ok'),
 ('VAV-0539', '10.101 CONSULTANT SPACE',        '10F-2', 'ok'),
 ('VAV-0540', '10.101 CONSULTANT SPACE',        '10F-2', 'ok'),
 ('VAV-0523', '10.031 COMM. DIR. DESIG.',       '10F-2', 'ok'),
 ('VAV-0524', '10.032 COMM. DIR. EDITOR',       '10F-2', 'ok'),
 ('VAV-0510', '10.018 PLANNING DIR. EXT. COORD','10F-2', 'ok'),
 ('VAV-0511', '10.019 SEN. POLICY ANALYST',     '10F-2', 'ok'),
 ('VAV-0512', '10.020 RESEARCH ANALYST',        '10F-2', 'ok'),
 ('VAV-0513', '10.021 RESEARCH ANALYST',        '10F-2', 'ok'),
 ('VAV-0514', '10.022 RESEARCH ANALYST',        '10F-2', 'ok'),
 ('VAV-0515', '10.023 HR OFFICER',              '10F-2', 'ok'),
 ('VAV-0516', '10.024 HR ASSISTANT',            '10F-2', 'ok'),
 ('VAV-0517', '10.025 PROCUR. REPRESENT',       '10F-2', 'ok'),
 ('VAV-0518', '10.026 SERVICE COORD',           '10F-2', 'ok'),
 ('VAV-0519', '10.027 SERV. SUPERVISOR',        '10F-2', 'ok'),
 ('VAV-0520', '10.028 FINANCE CONTROL',         '10F-2', 'ok'),
 ('VAV-0521', '10.029 SERV. DIR. TR. & GU. SERV.', '10F-2', 'ok'),
]

F11 = [
 # --- 11F-1 ------------------------------------------------------------------
 ('VAV-0553', '11.013 EXEC. DIR. CORR.',        '11F-1', 'ok'),
 ('VAV-0552', '11.012 PLANNING DIR.',           '11F-1', 'ok'),
 ('VAV-0579', '11.011 SECRETARY',               '11F-1', 'ok'),
 ('VAV-0578', '11.010 DIR. OF POL. & RES.',     '11F-1', 'ok'),
 ('VAV-0580', 'SHEIKHA WING BUSINESS LOUNGE',   '11F-1', 'ok'),
 ('VAV-0577', '11.009 SEC.',                    '11F-1', 'ok'),
 ('VAV-0576', '11.008 EXEC. DIR. CONSULTANT',   '11F-1', 'ok'),
 ('VAV-0602', '11.007 EXEC. DIR. CONSULTANT',   '11F-1', 'ok'),
 ('VAV-0575', '11.006 GIFT DIR.',               '11F-1', 'ok'),
 ('VAV-0604', 'SOUTH WEST CORRIDOR',            '11F-1', 'ok'),
 ('VAV-0574', '11.005 PROTOCOL DIR.',           '11F-1', 'ok'),
 ('VAV-0573', '11.004 ADM. ASSI.',              '11F-1', 'ok'),
 ('VAV-0571', '11.003 DIR. SHARED SERVICES',    '11F-1', 'ok'),
 ('FCU-0119', '11.531 IDF ROOM',                '11F-1', 'ok'),
 ('VAV-0554', '11.014 EXEC. DIR. CORR. MANAGER','11F-1', 'ok'),
 ('VAV-0555', '11.015 EXEC. DIR. CORR.',        '11F-1', 'ok'),
 ('VAV-0556', '11.016 LEGAL ASSIST.',           '11F-1', 'ok'),
 ('VAV-0557', '11.017 LEGAL ADVISOR',           '11F-1', 'ok'),
 ('FCU-0120', '11.531 IDF ROOM',                '11F-1', 'ok'),
 ('VAV-0581', 'SHEIKHA WING BUSINESS LOUNGE',   '11F-1', 'ok'),
 ('VAV-0605', 'HH WING BUSINESS LOUNGE',        '11F-1', 'ok'),
 ('VAV-0606', 'HH WING BUSINESS LOUNGE',        '11F-1', 'ok'),
 ('FCU-0121', '11.110 ELECT. CLOSET',           '11F-1', 'ok'),
 ('VAV-0568', '11.001 COMMUNICATION DIR.',      '11F-1', 'ok'),
 ('VAV-0570', '11.002 MED. REL. OFFICER',       '11F-1', 'ok'),

 # --- 11F-2 ------------------------------------------------------------------
 ('VAV-0559', '11.018 LEGAL ADVISOR',           '11F-2', 'ok'),
 ('FCU-0122', '11.108 PRINT COPY ROOM',         '11F-2', 'check'),
 ('FCU-0123', '11.106 MCC/ELEC ROOM',           '11F-2', 'check'),
 ('FCU-0124', '11.107 AV ROOM',                 '11F-2', 'ok'),
 ('VAV-0582', '11.201 SHEIKHA WING LOBBY',      '11F-2', 'ok'),
 ('VAV-0583', '11.201 SHEIKHA WING LOBBY',      '11F-2', 'ok'),
 ('VAV-0591', '11.204 SHEIKHA WING MEETING ROOM','11F-2', 'ok'),
 ('VAV-0590', '11.204 SHEIKHA WING MEETING ROOM','11F-2', 'ok'),
 ('VAV-0588', '11.203 SHEIKHA WING RELAX AREA', '11F-2', 'ok'),
 ('VAV-0589', '11.203 SHEIKHA WING RELAX AREA', '11F-2', 'ok'),
 ('VAV-0560', '11.019 DEP. EXEC. DIRECTOR',     '11F-2', 'ok'),
 ('VAV-0561', '11.020 EXEC. ASSI.',             '11F-2', 'ok'),
 ('VAV-0562', '11.021 EXEC. DIRECTOR',          '11F-2', 'ok'),
 ('VAV-0564', '11.022 SHEIKHA WING WAITING ROOM','11F-2', 'ok'),
 ('VAV-0603', 'SHEIKHA WING CORRIDOR 11.601',   '11F-2', 'ok'),
 ('VAV-0565', '11.022 SHEIKHA WING WAITING ROOM','11F-2', 'ok'),
 ('VAV-0567', '11.023 SECURITY ROOM',           '11F-2', 'ok'),
 ('VAV-0585', '11.208 SHEIKHA WING SHEIKHA ENSUIT', '11F-2', 'check'),
 ('FCU-0125', '11.512 IDF ROOM',                '11F-2', 'ok'),
 ('VAV-0584', '11.208 SHEIKHA WING SHEIKHA ENSUIT', '11F-2', 'check'),
 ('VAV-0587', '11.208 SHEIKHA WING SHEIKHA ENSUIT', '11F-2', 'check'),
 ('VAV-0586', '11.208 SHEIKHA WING SHEIKHA ENSUIT', '11F-2', 'check'),
]

RF = [
 ('FCU-0128', '12.003 MCC CLOSET',              'RF-1', 'ok'),
 ('FCU-0129', '12.003 MCC CLOSET',              'RF-1', 'ok'),
 ('FCU-0130', '12.004 MCC CLOSET',              'RF-1', 'ok'),
 ('FCU-0131', 'ROOF PLANT / WALKWAY (NEAR CSRR-0008)', 'RF-1', 'ok'),
 ('FCU-0126', '12.002 MCC CLOSET',              'RF-2', 'check'),
 ('FCU-0127', '12.002 MCC CLOSET',              'RF-2', 'check'),
]

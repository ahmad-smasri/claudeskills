#!/usr/bin/env python3
"""What "Included / Not included" means in the four registers, as a rule.

    python3 inclusion_rule.py            # measure the rule against the register
    python3 inclusion_rule.py --fill     # propose a verdict for every blank row

The verdict is set on the **room**, not on the equipment: 1,681 of the 1,692
rooms that carry one give the same answer for every unit serving them, and the
11 that do not are listed as exceptions rather than smoothed over. So the rule
takes a room name and returns Included or Not included, and every unit in that
room inherits it.

A room is **Not included** when it is one of:

  technical      plant, mechanical, electrical, IT and security rooms - IDF,
                 MDF, MCC, UPS, BMS, server, control room, AHU and plant rooms,
                 pump and sprinkler rooms, penthouses, the roof. All four
                 buildings.
  executive      the room of someone senior, or the en-suite, waiting room or
                 meeting room attached to one - director, manager, head of,
                 VP, president, executive, VIP, the Sheikha and HH wings. All
                 four buildings.
  (laboratory)   no building excludes laboratories. RDC's labs are Included.
                 The class is kept below, unused, because the register this
                 project started from did exclude them and someone will ask.
  common area    HQ only - corridors, lobbies, lounges, the spa, prayer and
                 ablution rooms, toilets, terraces, the cafeteria, the
                 visitors' centre.

Everything else is Included: the working office floor, open-plan and
workstation areas, secretaries and professional staff, meeting and print rooms,
stores, pantries, stairs and vestibules outside HQ.

The four token lists below are read off the register, not invented. Run without
arguments to see how far they reproduce it and which rooms they miss.
"""
import argparse
import collections
import csv
import re
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
SRC = HERE / 'All_Buildings_Rooms_Inclusion_Status_V1.3.xlsx'
TABS = (('HQ', 'HQ Asset Registry'), ('QNL', 'QNL Asset Registry'),
        ('SSC', 'SSC Asset Registry'), ('RDC', 'RDC Asset Registry'))
REPORT = HERE / 'inclusion_rule_report.csv'
FILLED = HERE / 'inclusion_proposed.csv'

# --- the four exclusion classes, as tokens that appear in a room name --------

TECHNICAL = """
 IDF MDF KDF MCC BMS GSM UPS QTEL SERVER PLANT MECH MECHANICAL ELEC ELECTRIC
 ELECTRICAL PENTHOUSE PENT.HOUSE SPRINKLER SPRIMKLERS PUMP PUMPS SUPPRESSION
 FIRE.COMMAND CHILLED.WATER VENT.PLANT CONTROL.ROOM CONTROL.CENTER SECURITY
 MISTING BATTERY FURNACE PIPE.CHASE CHASING RISER TELECOM COMMS
 AV.ROOM AV.IT ROOF PLANT.WALKWAY AHU.ROOM MACHINE.SHOP EL.SHOP WET/MECH LN2 UTILITY
 SERVICE.EQUIP SHARED.EQ CYBER.SERVER FLAMMABLE CYLINDER RECYCLING
 GENERAL.STORAGE FPC NOC PENT.HOUSE FURNACE PIPE.CHASE IT.SERVER
"""
EXECUTIVE = """
 DIRECTOR DIR EXEC EXECUTIVE PRESIDENT VP CHAIRMAN MANAGER MANAG HEAD ENSUIT
 BOD VIP SHEIKHA SHEIKA HH BOARD EXECOFFICE R&D
 *EXECDIR *COMMUNICDIR *SHSERVDIR *CONTRLDIR *DIRPROTOCOL
"""
LABORATORY = """
 LAB LABS PCR TC1 TC2 TC3 SEM MSCOPY MICROSCOPE CONFOCAL NMR ALD PLD
 SPUTTER EVAP MBE DESAL DESALINATION CSP HIGH.BAY ROBOTICS GENOM HISTOLOGY
 CYTO DNA RNA LENTIV QURNT SEQUENCE NANO PHOTOVOLTAIC OPTICAL CLEAN DIRTY PREP
 TEST.ROOM TESTING COLD.ROOM AIR.LOCK AIR.QUALITY ANALYT ANALYTIC ANALYTICAL
 ANALYSIS INTER.LAB SAMPLE.ACCESSION HY.ROOM GIS ELECTRO.PHYSICS ISOTOPE
 STEM MET/PROT SHAFALLAH DIABETES GENE.THERAPY BACTERLGY IMAGING IMMERSIVE
 CULTURE TISSUE CELL BIO CHEM SURF SERV.1 SERV.2 AAV A/L
 SEMINAR FLOW IPS-TC EM.PREP
"""
COMMON = """
 CORRIDOR LOBBY LOUNGE ENTRANCE WAITING RECEPTION SPA TREATMENT RELAXATION RELAX
 CHANGING TOILET WC PRAYER ABLUTION VESTIBULE TERRACE CAFETERIA DINING FITNESS
 SALON BRIDGE VISITOR OBSERVATION HEAT.EXP MULTI.PURPOSE PANTRY
"""

CLASSES = {'technical': TECHNICAL, 'executive': EXECUTIVE,
           'laboratory': LABORATORY, 'common area': COMMON}
# which classes each building excludes on
APPLIES = {
    'HQ':  ('technical', 'executive', 'common area'),
    'QNL': ('technical', 'executive'),
    'SSC': ('technical', 'executive'),
    'RDC': ('technical', 'executive'),      # laboratories are Included at RDC
}

# Equipment that serves plant rather than a room: it is not a room question, and
# every one of these already in the register is Not included.
PLANT_KIND = {'AHU', 'CHW Pump', 'DX Unit', 'EF', 'SEF', 'TEF', 'KEF', 'HEX',
              'CCU', 'Generator'}


# HQ writes a room as `<department> <role>`, and it is the role that decides.
# `STR PL DIR EXEC SECRE` is the strategic planning director's secretary and is
# Included; `STR PL DIR MANAGER` is not. So a junior role overrides the senior
# department in front of it - except an en-suite, which is always the senior's.
JUNIOR = """
 *SECRETAR *SECRET *SECRE *ASSIST *ARCHIVE *STAFF *CLERICAL *TRAINEES
 *ANALYST *AUDIT *CASHIER *PRINT *COPY *CEREMOFF *SCHED *SPACE *TECH *RECORD
 *UNIT *MEMBERS *CONSULTANT TR.AND.VIS
"""


def strip_number(room):
    """the room name without the number the client writes around it"""
    s = re.sub(r'^[A-Z]{0,3}\d*[.\-]?\d+[A-Za-z]?\s+', '', str(room).upper())
    s = re.sub(r'\s*[NSU]-\s?\d+[A-Za-z0-9]*\s*$', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def parse(group):
    """one regex per class - a dot in the token list means a space

    Whole words by default - `SPA` must not fire on `SHELL SPACE`. A token
    written with a leading `*` is matched anywhere in the name instead, for the
    handful of HQ departments the register runs into the role behind them
    (`COMMUNICDIRCOMM DESIGR`, `EXECDIREXECASSIST`).
    """
    parts = []
    for t in group.split():
        body = re.escape(t.lstrip('*').replace('.', ' '))
        parts.append(body if t.startswith('*') else r'\b%s\b' % body)
    return re.compile('|'.join(parts))


PARSED = {name: parse(g) for name, g in CLASSES.items()}
JUNIOR_RE = parse(JUNIOR)


def classify(building, room):
    """the class that excludes this room, or None if it is included"""
    name = strip_number(room)
    junior = JUNIOR_RE.search(name) and 'ENSUIT' not in name
    for cls in APPLIES.get(building, ()):
        if not PARSED[cls].search(name):
            continue
        if cls == 'executive' and junior:
            continue                     # the room belongs to the junior role
        return cls
    return None


def verdict(building, room, kind=''):
    """the verdict for one row, or a blank where there is no basis for one"""
    if kind in PLANT_KIND:
        return 'Not Included', 'plant equipment, not a room'
    if not str(room).strip() or 'NOT FOUND' in str(room).upper():
        return '', 'no room name - nothing to decide it on'
    hit = classify(building, room)
    return ('Not Included', hit) if hit else ('Included', '')


def load():
    """(building, tag, equipment type, verdict, room) for every asset"""
    wb = openpyxl.load_workbook(SRC, data_only=True)
    out = []
    for bld, tab in TABS:
        ws = wb[tab]
        out += [(bld, str(ws.cell(r, 1).value).strip(),
                 str(ws.cell(r, 2).value or '').strip(),
                 str(ws.cell(r, 3).value or '').strip(),
                 str(ws.cell(r, 4).value or '').strip())
                for r in range(3, ws.max_row + 1) if ws.cell(r, 1).value]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fill', action='store_true',
                    help='write a proposed verdict for every row with none')
    args = ap.parse_args()
    rows = load()

    # verdicts this script proposed on an earlier pass are not evidence of what
    # the client does - measuring against them would only measure the rule
    # against itself
    mine = set()
    if FILLED.exists():
        mine = {(r['building'], r['tag']) for r in csv.DictReader(FILLED.open())
                if r['proposed']}

    # the register's own room-level verdict, and where it contradicts itself
    byroom = collections.defaultdict(collections.Counter)
    for b, tag, kind, inc, room in rows:
        if room and inc and (b, tag) not in mine:
            byroom[(b, room)][inc] += 1
    split = {k: dict(c) for k, c in byroom.items() if len(c) > 1}
    truth = {k: c.most_common(1)[0][0] for k, c in byroom.items()}

    print('THE VERDICT IS SET ON THE ROOM')
    print('  %d rooms carry a verdict; %d of them disagree with themselves'
          % (len(truth), len(split)))
    for k, c in sorted(split.items()):
        print('     %-4s %-42s %s' % (k[0], k[1][:42], c))

    print('\nHOW WELL THE RULE REPRODUCES IT, room by room')
    report = []
    for b in ('HQ', 'QNL', 'SSC', 'RDC'):
        ok = miss = false = 0
        for (bb, room), want in truth.items():
            if bb != b:
                continue
            got, why = verdict(bb, room)
            if got == want:
                ok += 1
            elif want == 'Not Included':
                miss += 1
                report.append([b, room, want, got, 'rule includes it'])
            else:
                false += 1
                report.append([b, room, want, got, 'rule excludes it as %s' % why])
        n = ok + miss + false
        print('  %-4s %4d rooms | agrees %4d (%.1f%%) | rule says include, the '
              'register excludes %3d | rule says exclude, the register includes %3d'
              % (b, n, ok, 100 * ok / n, miss, false))

    print('\nWHY EACH EXCLUDED ROOM IS EXCLUDED')
    for b in ('HQ', 'QNL', 'SSC', 'RDC'):
        c = collections.Counter(
            classify(b, room) or 'no rule matches'
            for (bb, room), want in truth.items()
            if bb == b and want == 'Not Included')
        print('  %-4s %s' % (b, dict(c.most_common())))

    with REPORT.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['building', 'room', 'the register says',
                    'the rule says', 'note'])
        w.writerows(report)
    print('\nwrote %s (%d rooms where the two differ)' % (REPORT.name, len(report)))

    blank = [x for x in rows if not x[3] or (x[0], x[1]) in mine]
    print('\nROWS WITH NO VERDICT: %d' % len(blank))
    print('  %s' % dict(collections.Counter(x[0] for x in blank)))
    if not args.fill:
        print('  run with --fill to write the proposed verdicts')
        return
    with FILLED.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['building', 'tag', 'equipment type', 'room',
                    'proposed', 'why'])
        for b, tag, kind, _, room in blank:
            got, why = verdict(b, room, kind)
            w.writerow([b, tag, kind, room, got, why or 'no exclusion applies'])
    print('  wrote %s' % FILLED.name)
    prop = collections.Counter(verdict(b, room, kind)[0]
                               for b, tag, kind, _, room in blank)
    print('  proposed: %s' % dict(prop))


if __name__ == '__main__':
    main()

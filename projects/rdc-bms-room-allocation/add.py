#!/usr/bin/env python3
"""Append readings or blanks, from a compact spec on stdin.

    python3 add.py read  'North Building/FF/FF-5' <<'EOF'
    NB-VAV5510-EV5511 | Conference Room N-1101A | ok |
    EOF

Rows are appended, never rewritten, and a (screen, tag) already present is
skipped with a word rather than silently duplicated - the same reading made
twice from two crops of one screen would otherwise appear twice.
"""
import csv
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
FILES = {'read': ('readings.csv', ['screen', 'tag', 'room', 'confidence', 'note']),
         'blank': ('blanks.csv', ['screen', 'tag', 'reason'])}

kind, screen = sys.argv[1], sys.argv[2]
name, cols = FILES[kind]
path = HERE / name

rows = []
if path.exists():
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
seen = {(r['screen'], r['tag']) for r in rows}

added = skipped = 0
for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    parts = [p.strip() for p in line.split('|')]
    parts += [''] * (len(cols) - 1 - len(parts))
    row = dict(zip(cols, [screen] + parts[:len(cols) - 1]))
    if (row['screen'], row['tag']) in seen:
        skipped += 1
        continue
    seen.add((row['screen'], row['tag']))
    rows.append(row)
    added += 1

with path.open('w', newline='') as f:
    w = csv.DictWriter(f, cols, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print('%s: +%d added, %d already there, %d total' % (name, added, skipped, len(rows)))

#!/bin/sh
S="$1"
for f in "$S"/qnl_screens/*.jpg; do
  b=$(basename "$f" .jpg)
  [ -f "$S/out/${b}_all.json" ] && continue
  python3 annotate_all.py "$f" "$S/out/${b}_all.png" "$S/out/${b}_all.json" | sed "s|.*/out/|$b |"
done

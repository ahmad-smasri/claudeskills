#!/bin/sh
# trace the equipment icons on every screen not already done
S="$1"
for f in "$S"/qnl_screens/*.jpg; do
  b=$(basename "$f" .jpg)
  [ -f "$S/out/${b}_ic.json" ] && continue
  python3 annotate_icons.py "$f" "$S/out/${b}_ic.png" "$S/out/${b}_ic.json" | sed "s|.*/out/|$b |"
done

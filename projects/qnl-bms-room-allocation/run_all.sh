#!/bin/sh
# annotate every QNL screen; skip the ones already done
S="$1"
for f in "$S"/qnl_screens/*.jpg; do
  b=$(basename "$f" .jpg)
  [ -f "$S/out/$b.json" ] && continue
  python3 annotate_qnl.py "$f" "$S/out/$b.png" "$S/out/$b.json" | sed "s|.*/out/|$b |"
done

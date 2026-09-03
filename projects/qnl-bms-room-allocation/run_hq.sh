#!/bin/sh
# Trace every screen in one directory into another, skipping the ones already
# done so an interrupted run can be restarted. Written for the HQ screens but
# it takes both directories, so it works for any building:
#
#   ./run_hq.sh <screens dir> <output dir>
#
# `run_all.sh` is the QNL-shaped equivalent, with the paths built in.
S="$1"; O="$2"
for f in "$S"/*.jpg; do
  b=$(basename "$f" .jpg)
  [ -f "$O/${b}.json" ] && continue
  python3 annotate_all.py "$f" "$O/${b}.png" "$O/${b}.json" | sed "s|.*/${b}.png|$b|"
done

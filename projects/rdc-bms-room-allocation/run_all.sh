#!/bin/sh
# Trace every RDC screen. The annotated image and the tag strip beside it are
# what get read; the tracer only says where to look.
set -e
cd "$(dirname "$0")"
mkdir -p out
find screens -name '*.jpg' | sort | while read -r f; do
    rel=${f#screens/RDC/}
    name=$(printf '%s' "${rel%.jpg}" | tr '/ ' '__')
    python3 annotate.py "$f" "out/$name.png" "out/$name.json"
done

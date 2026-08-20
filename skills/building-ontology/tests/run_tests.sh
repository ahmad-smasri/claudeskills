#!/usr/bin/env bash
# Smoke tests for the ontology validator and the consistency checker.
#   ./tests/run_tests.sh
# Reads only .csv fixtures, so no openpyxl is needed.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
fail=0

echo "== the worked example must be clean"
if out=$("$PY" scripts/validate_ontology.py assets/example-minimal.csv 2>&1); then
    echo "   ok"
else
    echo "   FAIL: example-minimal.csv did not validate"
    echo "$out" | sed 's/^/   /'
    fail=1
fi

echo "== the broken fixture must trip every rule it was built to trip"
out=$("$PY" scripts/validate_ontology.py tests/broken-sample.csv 2>&1)
for code in E-TYP-2 E-LBL-1 E-PH-1 E-TYP-1 E-WS-1 E-PAIR-2 E-BN-1 E-GR-1 E-UNIT-1 \
            W-TYP-4 W-TYP-5 W-LBL-2 W-PT-1 W-GR-2; do
    if grep -q "$code" <<<"$out"; then
        echo "   ok   $code"
    else
        echo "   FAIL $code was not reported"
        fail=1
    fi
done

echo "== the worked example must be consistent"
if out=$("$PY" scripts/check_consistency.py assets/example-minimal.csv 2>&1); then
    echo "   ok"
else
    echo "   FAIL: example-minimal.csv reported consistency errors"
    echo "$out" | sed 's/^/   /'
    fail=1
fi

echo "== the inconsistent fixture must trip every consistency rule"
out=$("$PY" scripts/check_consistency.py tests/inconsistent-sample.csv 2>&1)
for code in E-CON-1 E-CON-2 E-CON-3 E-CON-4 E-CON-5 E-CON-6 E-CON-10 E-CON-17 \
            W-CON-7 W-CON-9 W-CON-11 W-CON-12 \
            I-CON-8 I-CON-13 I-CON-14 I-CON-15 I-CON-16; do
    if grep -q "$code" <<<"$out"; then
        echo "   ok   $code"
    else
        echo "   FAIL $code was not reported"
        fail=1
    fi
done

echo "== an empty template must validate"
"$PY" scripts/validate_ontology.py assets/ontology-template.csv >/dev/null 2>&1 \
    && echo "   ok" || { echo "   FAIL"; fail=1; }
"$PY" scripts/check_consistency.py assets/ontology-template.csv >/dev/null 2>&1 \
    && echo "   ok   consistency" || { echo "   FAIL consistency"; fail=1; }

echo
[ "$fail" -eq 0 ] && echo "all tests passed" || echo "tests failed"
exit "$fail"

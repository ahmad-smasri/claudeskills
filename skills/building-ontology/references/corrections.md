# Correcting a sheet that already exists

The skill has three jobs, not one. **Creating** a sheet is the first. **Validating**
one is the second. **Correcting** one - editing rows a previous pass or another
team delivered - is the third, and it is the one that can destroy work.

A creation bug produces a sheet that fails validation. A correction bug produces
a sheet that **passes** validation and is wrong: rows deleted that nobody asked
for, a join key rewritten, a point left with two classes. The validators cannot
save you here, because the output is well-formed. This file is the discipline
that replaces them.

Read this before editing any sheet you did not write in this session.

---

## 1. Baseline first, in numbers, before touching anything

Record what the sheet is now: row count, the full finding census per code (not
just the totals), and the counts of whatever family you are about to touch.

```bash
git show HEAD:path/to/sheet.xlsx > /tmp/base.xlsx        # or the delivered copy
python3 scripts/validate_ontology.py /tmp/base.xlsx --label-style verbatim | tail -1
python3 scripts/check_consistency.py /tmp/base.xlsx | grep -oE '\b[EWI]-CON-[0-9]+' | sort | uniq -c
```

**Compare the census afterwards, never only the totals.** A total that does not
move can hide one finding cleared and another created. Every code count should
be identical except the ones your change was meant to move, and you should be
able to name those before you run it.

## 2. Key on exact equality. Never a substring, never a prefix.

This is the rule that matters most, because every violation of it validates
clean afterwards. Three real near-misses, all in one project:

| removing | the trap | what a substring match destroys |
|---|---|---|
| `HW-Power-Thermal-Virtual-Meter` | `CHW-Power-Thermal-Virtual-Meter` **contains** it | all 360 chilled-water meters, 2,880 rows |
| `para:UPS_Meter` | rooms are **named** UPS and carry meters of their own | `entity:SSC_B-005_UPS_CHW-…`, `entity:QNL_B-084_UPS-Battery-Room_…` |
| `entity:SSC_AHUB0004_RA_P-Static` | it is a **prefix** of `…_RA_P-Static_01` and `_02` | both real return-air sensors |

So:

- match `r[0] == target` and `r[3] == target`, in both columns, against an
  explicit set of identifiers
- if you must match by shape, anchor on the separator - `subject.endswith("_" + segment)`
  is safe where `segment in subject` is not, because the character before `HW-Power`
  in `CHW-Power` is `C`, not `_`
- **name the targets in the script.** A list of four identifiers is auditable; a
  regex is not

## 3. The same shape can be right on one entity and wrong on another

`entity:SSC_AHUB0002_SA_P-Static` was surplus and had to go.
`entity:SSC_AHUB0001_SA_P-Static` is identical in shape and **correct** - that
AHU has one supply sensor and its point carries the reference row.

Never let the identifier pattern decide. Decide from the evidence - the IO list,
the reference row, the class - per entity, then name the ones that fail.

## 4. Assert what must survive, not only what must go

Every removal script should carry an explicit keep-list and check it after
building the output:

```python
for e in MUST_SURVIVE:
    if not any(r[0] == e or r[3] == e for r in out):
        raise SystemExit(f"{e} was destroyed - aborting")
```

That is what turns the prefix trap from a silent disaster into a refusal.

## 5. Count the block, not the row

Structures are multi-row and partial removal leaves debris that validates clean:

| structure | rows |
|---|---|
| a virtual meter with points | **8** - 4 structural, 2 `hasPoint`, 2 `ref:hasExternalReference` |
| a point | **2** - its `hasPoint` row and its reference row |
| `para:contributionFraction` on a unit | **2** |
| a class | 1 declaration, plus every cell that names it |

Assert the arithmetic: a removal should find *a whole number of blocks*, and
abort on anything else. Matching on the class alone finds 6 rows of a meter's 8,
because the two reference rows are subjected on the **points**, whose class
column names a sensor class, not the meter's.

## 6. A class lives in two cells per point

The class of a point appears twice: as the `objectType` of its `brick:hasPoint`
row and as the `subjectType` of its `ref:hasExternalReference` row. Change one
and the point has two classes - which `E-TYP-1` does catch, but only after you
have written it.

Retyping by class alone is how that happens: a filter on
`brick:Thermal_Energy_Usage_Sensor` matches every point of that class in the
sheet, not the family you meant. **Scope a retype to an explicit set of points**,
then assert both sides agree for each one.

## 7. Build type maps from both columns

An entity can be declared purely as the **object** of a row and be the subject of
nothing. SSC's FCU cooling valves are exactly that: `CHW-Coil --brick:hasPart-->
CHW-Coil_Valve`, and the valve carries nothing of its own.

A type map built as `{r[0]: r[1] for r in rows}` misses all of them, and the
answer to "does this unit have a valve?" comes back a confident, wrong **no**.
Read `(r[0], r[1])` **and** `(r[3], r[4])`.

## 8. Guards assert "no new", not "none"

A delivered sheet arrives with defects. A guard that demands zero blocks
legitimate work on the first run and tempts you to delete the guard.

```python
before, after = orphaned(body), orphaned(out)
if after - before:
    raise SystemExit(f"newly orphaned: {sorted(after - before)} - aborting")
```

Report the pre-existing count so it stays visible and cannot quietly grow.

## 9. Dry run, then read the numbers before you write

Every correction script takes `--dry-run` and prints what it would do, per row.
Read it against what you predicted. Two real saves this way:

- a retype reported **414 cells** where 72 were intended - it had caught 342
  points of another family and rewritten one side of each, leaving them
  half-typed, which is worse than either end state
- a removal reported **9 rows** where 49 were intended - the matcher only knew
  the building-tier identifier and would have silently left five floors behind

Both were invisible in the totals and obvious in the per-row output.

## 10. Do not silently fix what you were not asked about

Finding a second defect while fixing the first is normal. Fixing it without
saying so is not: it lands unreviewed in a client deliverable, and the diff no
longer matches the request.

Report it, name the fix, and let the owner call it. Where the defect is in
delivered data, that is their decision every time. What you **must not** do is
leave it unrecorded - put it in the assumption log with the evidence, so it
survives the conversation.

## 11. Numbers in prose rot faster than rows

Every count in a handover note, an assumption log entry or a reference file is a
claim that goes stale the moment a later pass changes the sheet. One note in this
project claimed `1,459 meters, 8,754 rows` when the sheet held 1,460 and 11,680 -
wrong on both, and one of them accidentally right again two changes later.

When a pass changes a count, grep the repo for the old number and fix every
instance in the same commit. If a figure describes a dated step rather than the
current state, say which - "the layer added 5,568 rows" survives; "the sheet has
5,568 rows" does not.

---

## The checklist

```
[ ] baseline recorded: rows, per-code census, family counts
[ ] targets named explicitly, matched by exact equality in both columns
[ ] keep-list asserted to survive
[ ] block arithmetic asserted (8 rows a meter, 2 rows a point)
[ ] both cells per point when a class changes
[ ] type maps read subject AND object columns
[ ] guards compare before/after, not against zero
[ ] --dry-run output read line by line and matched to the prediction
[ ] after: census compared per code, only the intended codes moved
[ ] every incidental defect found is reported, not silently fixed
[ ] every stale count in prose updated in the same commit
```

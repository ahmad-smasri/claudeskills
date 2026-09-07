# Resolving a class

Run this ladder for every equipment, part and point. Stop at the first step that
answers.

## 1. Is it in Dar Cairo?

```
python3 scripts/lookup_reference.py --class "booster pump"
python3 scripts/lookup_reference.py --template brick:Fan_Coil_Unit
```

`--class` fuzzy-matches class names in the primary reference. `--template` shows
what a complete instance of that class looks like: the parts, points and
properties it normally carries, with the share of instances that have each, plus
one worked example.

If Dar Cairo has the class, reuse it exactly. Consistency with the primary
reference is worth more than a marginally better class choice.

## 2. Is it in Brick?

```
python3 scripts/lookup_reference.py --term Heat_Wheel
```

This checks the full Brick 1.4 term list - 2,587 classes and properties, with
deprecation and alias status. Also browse <https://ontology.brickschema.org>;
Brick has far more classes than people expect.

Two traps:

- **Aliases.** Brick keeps `brick:AHU`, `brick:VFD`, `brick:HVAC_System` for
  backwards compatibility, but each has a preferred form
  (`brick:Air_Handling_Unit`, `brick:Variable_Frequency_Drive`,
  `brick:Heating_Ventilation_Air_Conditioning_System`). Use the preferred one.
  The validator warns (`W-TYP-5`) and names the replacement.
- **Deprecated terms.** 246 terms are deprecated, mostly spatial classes moved to
  REC, plus water points where supply/return became entering/leaving. `W-TYP-4`
  carries Brick's own mitigation message. A deprecation usually ships a functional
  replacement (supply/return → entering/leaving for water), so migrating to the
  replacement is the default. Keeping the deprecated class is a reviewer's call -
  when they make it, keep the class and add a `note` naming the current
  replacement, so the row still documents the move.

## 3. Is it in a previous project's ontology?

Before coining anything, check the ontologies already delivered for other
projects. They are in `reference-models/`:

```
python3 - <<'PY'
import openpyxl
wb = openpyxl.load_workbook('reference-models/QF_SSC_Ontology_V03.xlsx', data_only=True)
ws = wb['SSC_Ontology_Ver0.6']
hits = {ws.cell(r,2).value for r in range(2, ws.max_row+1)
        if 'YourKeyword' in str(ws.cell(r,2).value)}   # subjectType column
print(sorted(hits))
PY
```

`QF_SSC_Ontology_V03.xlsx` (the QF SSC building) is the first to check - it is
the current house sheet and carries the 27-column shape we deliver (Dar
Cairo itself went to 33 at V98).
`QF_HQ_Ontology_draft0.4.xlsx` (the QF HQ building, 28,929 rows) is the second -
read it for class and structure precedent, not for units (several of its rows
carry a wrong `brick:hasUnit`), and pick its sheet by the header contract, not by
its misspelled tab `HQ_Onotlogy_Draft_v0.4`. Later projects go here too as they
land.

Why this sits above minting a `para:` class: a previous project has usually
already faced the same gap and coined a `para:` class for it. **Reuse that exact
class - do not mint a parallel one.** Worked precedent from SSC: fan trip/failure
alarms are split by point name into `para:Fail_Start_Alarm` and
`para:Fail_Stop_Alarm`; room air temperature is `brick:Room_Air_Temperature_Sensor`;
speed feedback is `brick:Speed_Sensor`. When SSC's class is itself `para:`, the
row's source is the previous project, not a fresh mint - it still goes in the
handover note, flagged as already-in-SSC rather than new.

If no previous project has it either, fall through to step 4.

## 4. Not anywhere above: make a `para:` subclass

Pick the **most specific correct parent** - that is what makes the new class
inherit the right properties and stay discoverable to applications.

```
para:Pressure_Independent_Module | owl:Class | rdfs:subClassOf | brick:Terminal_Unit |
| rdfs:label_en | Pressure Independent Module
```

Rules:

1. Namespace it `para:`. Never `brick:` or `rec:`.
2. `subjectType` is `owl:Class`.
3. The parent is a real `brick:`, `rec:` or existing `para:` class.
4. Give it an `rdfs:label_en`.
5. Define it once, at the top of the sheet, before first use.
6. It goes to the PARA team for review before entering the shared extension
   `.ttl` - list it in the handover note.

Check `references/data/para-classes.csv` first - 228 `para:` classes already
exist across the reference models. Reuse beats minting.

**New properties** use the same shape but `rdfs:subPropertyOf`, with
`subjectType` `brick:EntityProperty`, `owl:ObjectProperty` or
`owl:DatatypeProperty`:

```
para:ratedChilledWaterFlowrate | brick:EntityProperty | rdfs:subPropertyOf |
brick:EntityProperty | | rdfs:label_en | Rated Chilled Water Flowrate
```

## 5. No sensible parent: root it at `brick:Point`

When the thing has no superclass anywhere in Brick, define a new `owl:Class` as
`rdfs:subClassOf brick:Point`. Dar Cairo has precedent for this shape, so check
there for a match before adding one.

**This applies to points only.** If the orphan is a piece of equipment, stop and
ask the user which root to put it under:

> `<name>` has no equivalent in Brick 1.4 and no obvious parent class. It is
> equipment, not a point, so `brick:Point` is the wrong root. Which should it sit
> under - `brick:Equipment`, `brick:HVAC_Equipment`, `brick:Electrical_Equipment`,
> or something else?

Do not pick a root to make the row validate. A piece of equipment filed under
`brick:Point` breaks every application that queries equipment.

## Never use a root class as a catch-all: `brick:Alarm`

`brick:Alarm` is the root of the alarm tree, not a bucket for every alarm point.
**Only a point whose name or label is literally a general / summary / common alarm
is typed `brick:Alarm`.** Every other alarm - trip, fail-to-start, fail-to-stop,
overload, phase-loss, high-level, filter, communication-loss - is a specific alarm
and runs the full ladder like any other point:

1. Dar Cairo (e.g. `para:Phase_Loss_Alarm`, `para:High_Level_Alarm` already exist there);
2. Brick 1.4 (`brick:Overload_Alarm`, `brick:Communication_Loss_Alarm`, `brick:Air_Flow_Alarm`, …);
3. a previous project (SSC coined `para:Fail_Start_Alarm`, `para:Fail_Stop_Alarm`, `para:Summary_Alarm` under `brick:Alarm`);
4. only if none has it, a new `para:<Name>_Alarm rdfs:subClassOf brick:Alarm`.

The failure mode this prevents is real and in the reference data: SSC types its
own `_TripAlm` points as the bare `brick:Alarm`, so a query for "trip alarms"
cannot tell them apart from any other alarm. QNL splits them out as
`para:Trip_Alarm` instead. Distinguish alarms by point name; reserve `brick:Alarm`
for the one that genuinely is general.

The same reasoning applies to any other root or near-root class -
`brick:Sensor`, `brick:Setpoint`, `brick:Status`, `brick:Command`, `brick:Point`
itself. Reach for the root only when the point really is that generic; otherwise
resolve it to the specific class through the ladder.

## Where the classes came from

| List | Contents | Rebuild with |
|---|---|---|
| `data/brick-vocab.txt` | every Brick 1.4 / REC / ref term, with deprecation and alias status | `scripts/build_brick_vocab.py Brick.ttl` |
| `data/brick-rec-vocab.txt` | the 193 terms with actual precedent in Dar Cairo | `scripts/build_vocab.py` |
| `data/para-classes.csv` | 228 `para:` classes and their parents | `scripts/build_vocab.py` |
| `data/para-properties.csv` | 13 `para:` entity properties | `scripts/build_vocab.py` |
| `data/units.csv` | units seen with `brick:hasUnit`, with usage counts | `scripts/build_vocab.py` |

To refresh the Brick list against a newer release:

```
pip download --no-deps -d /tmp/bs brickschema
unzip -q /tmp/bs/brickschema-*.whl -d /tmp/bs/x
python3 scripts/build_brick_vocab.py /tmp/bs/x/brickschema/ontologies/1.4/Brick.ttl
```

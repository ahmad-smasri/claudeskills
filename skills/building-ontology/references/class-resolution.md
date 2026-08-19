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
  carries Brick's own mitigation message.

## 3. Not in Brick: make a `para:` subclass

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

## 4. No sensible parent: root it at `brick:Point`

When the thing has no superclass anywhere in Brick, define a new `owl:Class` as
`rdfs:subClassOf brick:Point`. Dar Cairo has precedent for this shape, so check
there for a match before adding one.

This applies to **points**. If the orphan is a piece of equipment rather than a
point, `brick:Point` is the wrong root - stop and ask which root to use rather
than filing equipment under Point.

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

# Naming and labels

## First: source identifiers, or the convention? Ask.

Source sheets usually arrive with identifiers already assigned - a room schedule
column literally headed `Room Entity Name`, an asset register whose tags match
the BMS. **Those strings are a join key.** SCADA, the assets register, the room
schedule and the client's own drawings all key off them; rename them and every
one of those joins has to be rebuilt by hand.

So before naming anything, ask:

> Your rooms/assets already carry identifiers - `entity:QNL_B_063_PLANT_ROOM_01`,
> `VAV_B_S11_024`. Do you want those kept exactly as they are, or normalised to
> the PARA convention (`QNL_B_PLANT-ROOM-01_063`, `VAV-B-S11-024`)? Keeping them
> preserves the join back to your source sheets and SCADA; normalising matches
> the documentation.

**Default to keeping the source identifiers** when the source supplies them.
That is the house preference: the convention below governs identifiers *this
sheet has to invent* - site, building, levels, systems, virtual meters, parts and
points - not identifiers the client already owns.

When keeping source identifiers, the only edits taken unasked are the ones the
validator forces: strip leading and trailing whitespace (`E-WS-1`) and remove
embedded spaces (`E-SPACE-1`). Do not expand abbreviations, reorder segments, or
swap underscores for dashes. Labels are where the cleanup happens - the label
rule below applies regardless of how the identifier is spelled.

### Misspellings are a separate question, and the user's to answer

A schedule typed by hand carries typing errors, and an identifier is not the
only thing they damage: the same string becomes the `rdfs:label_en` a user reads
on screen, so `STUDENT CARRLES` and `L1.130 PUBLIS SPACE` ship to the front end.
Correcting them is not the same decision as normalising an identifier's shape,
so **ask about it separately at intake** - the intake question is in
`intake.md`. On QNL the answer was to correct them; the default until asked is
to leave them and report them.

When the answer is to correct:

- **Only where the sheet itself proves the correction.** The right spelling
  already appears on a sibling (`CARRELS` on 15 other rooms, `L1_042_LOBBY`
  against `B_145_LOBY`), or the token is two words run together whose separator
  every other room writes (`REST_ROOMMEN` against nine `REST_ROOM_MEN`).
  Anything you are reasoning towards rather than reading off another row is a
  question for the user, not a fix.
- **Whole tokens only**, so a correction cannot fire inside a longer word, and
  the abbreviations the schedule uses deliberately - `AD`, `SEC`, `RES`, `LIBR`,
  `PERS` - survive untouched. Correcting a misspelling is not the same as
  expanding an abbreviation; the second is a rewrite and needs asking.
- **The name segment only.** Never the level or the room number, and never an
  asset tag: those are the join key back to the drawings and to the BMS.
- **From one map, in the build script**, so identifier and label are still
  derived from the same corrected string and cannot drift apart. Every entry
  carries the evidence beside it as a comment.
- **Never a `ref:hasTimeseriesId`, a `rec:modelNumber`, or any other database
  key.** Building vocabularies are full of strings that read as typos and are
  not - `NBONEOB` is a Nuaire model number, `SupPreFlt` and `MinFALoocupTb` are
  SCADA keys that must match the historian character for character. Pair every
  candidate with its property name before touching it.
- **Record the whole list in the handover note**, and regenerate the identifier
  crosswalk. The source's own strings no longer match the ontology, so the
  crosswalk is what keeps that join documented rather than lost.

Find them by extracting the distinct word tokens across every subject, object
and label - a few hundred, for a building - and reading each non-word token back
in its own row. A dictionary is the wrong tool: it drowns in the abbreviations.

### The building code goes in front, on everything

QF SSC prefixes every subject with the building code - `entity:SSC_FCU0001`,
`entity:SSC_01_001_CORRIDOR`. Follow it: `entity:QNL_FCU_1F_056`,
`entity:QNL_AHUB011`. Rooms usually arrive with the code already in the source
entity name; asset registers usually do not, because the BMS only needs the tag
unique within one building. **Add the code, leave the tag itself alone** - it
stays the join key - and carry the same prefixed form into `rdfs:label_en` and
`ref:ifcName`, as SSC does.

### The site is the organisation's code, and buildings share it

QF SSC's current sheet opens with one row for the whole spatial hierarchy above
the levels:

```
entity:SSC | rec:Building | rec:isPartOf | entity:QF | rec:Site
           | rdfs:label_en | SSC Building | rdfs:label_en | Qatar Foundation
```

Three things to copy. The **site identifier is the organisation's code**,
`entity:QF`, not its spelled-out name - the name lives in the label. The
**building label is `<code> Building`**, so `SSC Building`, `QNL Building`. And
**every building under the same client reuses the same site entity**: QNL is in
Qatar Foundation too, so it points at `entity:QF` rather than minting a second
name for the same site. Mint a second one and the two sheets no longer join when
the converter loads them into one graph.

```
entity:QNL | rec:Building | rec:isPartOf | entity:QF | rec:Site
           | rdfs:label_en | QNL Building | rdfs:label_en | Qatar Foundation
```

**Ask which site entity the client already uses** before inventing one. It is
the one identifier in the sheet that is shared across projects, so it is the one
most likely to already exist somewhere you cannot see.

**Shared plant is the exception, and both reference models agree on it.** A
system, a loop or a riser serves the building rather than sitting inside it, and
neither model gives it a building code:

| | Shared plant |
|---|---|
| QF SSC | `entity:HVAC`, `entity:CHW-System` |
| Dar Cairo | `entity:CHWS-LOOP-1`, `entity:CHWS-LOOP-2`, `entity:Water_System` |
| QNL | `entity:QNL_CHWS-MAIN-LOOP` |

Bare name, dashes, no prefix - a system serves the site or the building rather
than sitting in it. **The exception is a per-building asset that would collide
across sheets.** QF SSC 0.5 writes `entity:CHWS-MAIN-LOOP` bare while also
declaring it `rec:locatedIn entity:SSC`; a second building reusing that name
yields one loop located in two buildings the moment both sheets load into one
graph. QNL therefore prefixes its own: `entity:QNL_CHWS-MAIN-LOOP`. Prefix when
the entity is per-building, leave bare when it is genuinely shared, and say which
you did. `check_consistency.py` knows this and
exempts the objects of `brick:isPartOf` and `rec:isFedBy` from its
missing-prefix check.

Dar Cairo and QF SSC 0.5 both declare the loop with a `rec:locatedIn` row
pointing at the building, which is worth copying - it is where the loop's label
lives. Neither declares `entity:HVAC` or `entity:CHW-System` with a label of its
own, so `W-LBL-2` fires on them; give yours a label.

### Audit the source identifiers for consistency, and report what you find

**"Keep them verbatim" assumes they are internally consistent. Check that they
are, before writing rows.** Read the whole column, not the first ten values, and
work out the shape the majority follow; then list every row that departs from it.
A schedule maintained by hand over years drifts, and a sheet that inherits the
drift is harder to query than the source was.

**Audit the asset register the same way, family by family.** Reduce every tag to
a shape (digits to `#`), count the shapes, and name the families that do not
match the others. QNL's assets: VAV `VAV_<level>_S<system>_<count>` and CAV the
same, FCU `FCU_<level>_<count>` with no system segment, and AHUB `AHUB<count>`
with no separators and no level segment at all - one family out of four with a
different structure, plus a single tag, `VAV_1F_S15_039S`, breaking its own
family with a trailing letter. Asset tags are usually the BMS join key, so
expect the answer to be "report it, change nothing"; report it anyway, because
the register's owner is the one who can fix the register.

QNL's rooms: 285 of 336 wrote the level and the room number as separate segments,
`QNL_B_034_MEETING_ROOM`. The other 51 ran them together or used a different
separator - `QNL_B036_REST_...`, `QNL_B-ST-01_...`, `QNL_L1023_1_...`. There the
answer was to rebuild the whole column to one shape.

**Report the exceptions and ask; do not silently normalise, and do not silently
keep them.**

> 51 of your 336 room identifiers use a different shape from the other 285:
> `QNL_B036_REST_REST_ROOM_WOMEN` and `QNL_B-ST-01_ST-01` against the majority
> `QNL_B_034_MEETING_ROOM`. Do you want them regularised to the majority shape,
> or kept exactly as the schedule has them?

Give the count, one example of each variant, and the majority shape. When they
choose regularisation, rebuild the identifier and the label from the same parsed
segments so the two cannot drift apart, and ship the crosswalk.

Record the answer in the handover note, and ship a crosswalk file
(`source_identifier, ontology_identifier, label`) whenever any identifier
changed shape.

## Identifiers

| Level | Pattern | Example |
|---|---|---|
| Site | `Site-Name` | `Smart-Village` |
| Building | `Building-Name` | `Dar-Cairo`, `150H` |
| Level | `Building-Name_Floor-XX` | `Dar-Cairo_Floor-1`, `Dar-Cairo_Basement-2` |
| Room | `Building-Name_Floor-XX_Room-Name_Number` | `Dar-Cairo_Ground-Floor_TECH-3_G007` |
| HVAC zone | `Building-Name_Floor-XX_HVAC-Zone` | `Dar-Cairo_Floor-1_1HC-H1` |
| Parent zone | `Building-Name_Floor-XX_Parent-Zone` | `Zone-A`, `Dar-Cairo_Ground-Floor-C` |
| Equipment | `Equipment-Type-Floor-Count` | `AHU-B1-02`, `CHWP-B1-1-PUMP-7-LEFT` |
| Equipment part | `Equipment_Part` | `AHU-B1-02_SF` |
| Point | `Equipment_Part_Point` | `AHU-B1-02_SF_VFD_Elec-Demand` |

This table is what to use when **no source identifier exists**. When one does,
see the section above.

Worked breakdowns:

- `AHU-B1-02` = type `AHU` + floor `B1` + count `02`
- `CHWP-B1-1-PUMP-7-LEFT` = type `CHWP` + floor `B1-1` + unique ID `PUMP-7-LEFT`

## Character rules

- **Dashes separate words** inside a segment: `Dar-Cairo`, not `dar cairo` or `darCairo`
- **Underscores separate segments**: `Dar-Cairo_Basement-3_Pump-Room_B331`
- **No spaces anywhere** in an identifier, class name or property name
- **Case is significant**: `rec:Building` is not `rec:building` or `Rec:Building`.
  Brick classes are `Title_Case_With_Underscores`; properties are `camelCase`
- **Abbreviations only if industry-standard**: AHU, FCU, VAV, CRAC, CHWP, VFD, UPS

The PARA document writes the equipment format with underscores
(`<Type>_<Floor>_<ID>`) but both of its own examples, and all of Dar Cairo, use
dashes. Follow the examples: dashes.

### Naming datapoints the Dar Cairo way

When a client asks for identifiers aligned to Dar Cairo (the *normalise* path
above), or whenever the sheet **invents** point identifiers, follow Dar Cairo's
exact convention. It is one rule, applied per segment:

- **`_` separates segments** - equipment, then component, then point:
  `AHU-B-001_CHW-Coil`, `HEX-01_Iso-Vlv_Open-Close-Status`.
- **`-` separates words inside a segment**: `CHW-Coil`, `Trip-Status`,
  `Room-Air-Temperature-Setpoint`. No camelCase, no dots, no spaces.
- **A datapoint is named in dashed English, not the BMS token.** Dar Cairo writes
  `_Trip-Status`, `_Open-Close-Status`, `_Temperature` - never `_TripAlm` or
  `_RmTempSP`. Take the name from the point's own `rdfs:label_en` when it is
  clean English (`Average Space Humidity` → `Average-Space-Humidity`); when the
  label is a raw token (`RunSts`, `IsoVlv AutoManCmd`), take it from the point's
  **Brick/para class** instead (`brick:Run_Status` → `Run-Status`,
  `para:Auto_Manual_Command` → `Auto-Manual-Command`). Either way no camelCase
  survives.
- **A part of a part extends the parent's segment with `-`** (`_SF` → `_SF-Motor`,
  Dar Cairo's `FCU-9_F5_SF-Motor`); **a point opens a new `_` segment** off
  whatever owns it.

Name identifiers this way as you emit them - it is one function over the label or
class. `scripts/align_naming.py` is the retrofit for a sheet already built with
raw/BMS identifiers: it classifies every entity from the graph, renames from the
label-or-class, and applies one consistent bijection to both identifier columns,
writing an old → new crosswalk. Run it once (it is not idempotent).

**The BMS join keys never move.** `ref:hasTimeseriesId` and `para:hasEntityId`
keep the raw historian tag character-for-character, and `ref:ifcName` is
regenerated from the new id. The identifier is internal; the join lives in the
timeseries reference and the crosswalk, exactly as Dar Cairo's own dashed ids
differ from the raw SCADA tags they carry. QNL was normalised this way:
`QNL_AHU_B_001_AvgSpcHumd_PV` → `QNL_AHU-B-001_Average-Space-Humidity`, 71% of
ids camelCase → 0%, with rooms and levels kept in the verbatim spatial style.

## Labels

`rdfs:label_en` is what the front end displays. Every entity a user will see
needs one.

**Two styles are in use. Ask which one before writing rows**, the same way you
ask about identifiers:

> Labels: the PARA label rule strips punctuation, so `1.001_CORRIDOR` becomes
> `1.001 CORRIDOR`. QF SSC instead carries the source text verbatim -
> `1.001_CORRIDOR`, `SSC_FCU0001`. Which do you want?

| Style | `rdfs:label_en` for room `B_063` / `PLANT_ROOM_01` | Validator |
|---|---|---|
| `verbatim` - QF SSC house style | `B.063 PLANT ROOM 01` | `--label-style verbatim`, `E-LBL-1` off |
| `para` - the label rule below | `B 063 PLANT ROOM 01` | default, `E-LBL-1` enforced |

**`verbatim` is the source text with underscores read as word breaks, and every
other mark left alone.** That is the one edit: `_` becomes a space. The dot
between the level and the room number survives, and so do dashes and slashes -
SSC keeps `A / V ROOM` exactly as the schedule wrote it. The room-label shape is
therefore `<level>.<number> <name>`: SSC writes `1.001 CORRIDOR` for room 001 on
level 1, QNL writes `B.063 PLANT ROOM 01` for room 063 in the basement.
Equipment keeps its register tag with the same treatment: `SSC_CHW_CHWP01 Motor`,
`QNL VAV B S11 024`.

The two styles differ in how much they remove, not in kind. `verbatim` removes
one character class; `para` removes every punctuation mark except a decimal point
between two digits. On a label with no underscores the two agree.

**Route every label through one function.** QNL's loop label kept its
underscores for a build because it was written as a literal instead of passing
through the labeller - a rule applied in one place is a rule with a hole in it.

**QF SSC is the recent completed sample and it uses `verbatim` throughout** -
rooms labelled `1.001_CORRIDOR`, `1.008_A / V ROOM`, equipment labelled with the
raw register tag `SSC_FCU0001`. Dar Cairo is a third thing again
(`Mechanical-Area-2-R014`). Neither reference model satisfies the label rule, so
do not infer the answer from precedent - ask, then pass the matching
`--label-style` to the validator and say which style the sheet uses in the
handover note.

In `verbatim` style the only edit is stripping whitespace, which the validator
rejects regardless (`E-WS-1`).

### The PARA label rule

**The rule: letters, digits and spaces. A decimal point survives between two
digits. Every other punctuation mark is removed.**

| Raw source name | Label |
|---|---|
| `1.001_CORRIDOR` | `1.001 CORRIDOR` |
| `Mechanical-Area-2_R014` | `Mechanical Area 2 R014` |
| `Coefficient of Performance (COP)` | `Coefficient of Performance COP` |
| `PM2.5 Sensor` | `PM2.5 Sensor` |
| `W-WC_G004` | `W WC G004` |

Separators - `_ - . / \` - become a single space; everything else non-alphanumeric
is dropped; runs of spaces collapse. `scripts/validate_ontology.py` reports the
offending characters and the corrected string (`E-LBL-1`), and
`clean_label()` in that script is the reference implementation. Under
`--label-style verbatim` the rule is not applied and `E-LBL-1` never fires.

This rule is newer than Dar Cairo, so the primary reference does not satisfy it -
about 3,200 of its labels carry dashes, underscores or brackets. Follow the rule
for new work; do not copy Dar Cairo's labels verbatim.

## IFC references

Anything that must appear in the 3D/BIM view needs an IFC reference. It is not a
column - it is a row, using the external-reference shape:

```
entity:UPS-02 | brick:Energy_Storage | ref:hasExternalReference | <blanknode> |
ref:IFCReference | | | ref:ifcName | UPS-02
```

The `ref:ifcName` value is the subject name without the `entity:` prefix and
without spaces.

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

When keeping source identifiers, the only permitted edits are the ones the
validator forces: strip leading and trailing whitespace (`E-WS-1`) and remove
embedded spaces (`E-SPACE-1`). Do not fix typos, expand abbreviations, reorder
segments, or swap underscores for dashes. Labels are where the cleanup happens -
the label rule below applies regardless of how the identifier is spelled.

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
| QNL | `entity:CHW-Loop` |

Bare name, dashes, no prefix. The building code marks what is *in* this building;
a chilled water loop feeding it is not. `check_consistency.py` knows this and
exempts the objects of `brick:isPartOf` and `rec:isFedBy` from its
missing-prefix check.

Dar Cairo declares the loop with a `rec:locatedIn` row pointing at the building,
which is worth copying - it is where the loop's label lives. QF SSC never
declares `entity:HVAC` or `entity:CHW-System` as a subject at all, so they carry
no label and `W-LBL-2` fires on them.

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
| `verbatim` - QF SSC house style | `B.063_PLANT_ROOM_01` | `--label-style verbatim`, `E-LBL-1` off |
| `para` - the label rule below | `B 063 PLANT ROOM 01` | default, `E-LBL-1` enforced |

**The SSC room-label shape is `<level>.<number>_<name>`** - a dot between the
level and the room number, an underscore before the name. SSC writes
`1.001_CORRIDOR` for room 001 on level 1; QNL writes `B.063_PLANT_ROOM_01` for
room 063 in the basement. Equipment carries its raw register tag with no
reshaping: `SSC_FCU0001`, `VAV_B_S11_024`.

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

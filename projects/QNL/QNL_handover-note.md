# QNL ontology — handover note

**Deliverable:** `QNL_Ontology.xlsx` (also `QNL_Ontology.csv`) — 2,577 rows on the
27-column PARA header. Validate with
`validate_ontology.py QNL_Ontology.xlsx --label-style verbatim`. Supporting file: `QNL_identifier_crosswalk.csv`, listing every
source identifier against the identifier used in the sheet and its label.

**Sources:** `QNL_Room_Names_for_Ontology.xlsx` (336 rooms),
`QNL_Assets_Location_Relationships.xlsx` (449 assets across AHUB / VAV / CAV / FCU).

## What is in the sheet

| Layer | Rows | Content |
|---|---|---|
| Extensions | 1 | `para:Chilled_Water_Loop_Network` |
| Site + Building | 1 | `entity:QNL` `rec:isPartOf` `entity:QF` |
| Levels | 4 | `entity:QNL_B` → "Basement", `_L1` → "Level 1", `_L2` → "Level 2", `_T1` → "Terrace 1" |
| Rooms | 336 | each `rec:isPartOf` its level |
| Systems | 2 | `entity:HVAC` `brick:isPartOf` `entity:QF`; `entity:CHW-System` under it |
| Chilled water loop | 3 | `entity:QNL_CHWS-MAIN-LOOP` — `brick:isPartOf` CHW-System, `rec:locatedIn` the building, + IFC reference |
| Equipment | 2,230 | 15 AHU, 246 VAV, 51 CAV, 137 FCU |

Per asset: `rec:locatedIn` → its room, `brick:isPartOf` → `entity:HVAC`,
`rec:isFedBy` → its upstream source,
`ref:hasExternalReference` → an `ref:IFCReference` blank node, and for the terminal units
(VAV, CAV, FCU) `rec:feeds` → the room it serves. AHUs get no `rec:feeds` row — see "one
direction" below.

## Decisions taken, per your answers

**Predicate direction — one direction, held throughout.** Equipment-to-equipment links
are always stated as `rec:isFedBy` (downstream names its source); equipment-to-space
links are always stated as `rec:feeds` (terminal unit names the room it serves). No link
is stated twice. The AHU → VAV/CAV chain therefore appears once, on the VAV/CAV row:
`entity:VAV_B_S11_024 rec:isFedBy entity:AHUB011`. AHUs have no `rec:feeds` row
because they do not serve a room directly — the 297 VAV/CAV rows carry that chain.

**Room Tag used for both `rec:locatedIn` and `rec:feeds`** on terminal units; for AHUs
it is a plant room, so `rec:locatedIn` only. 53 VAVs carry a level token that differs
from the level of their room — e.g. `entity:VAV_2F_S12_001` against
`entity:QNL_L1_001_OPEN_READING_AREA`. You confirmed these are open-roof spaces running
from the served level up to the level the box sits on, so the unit is genuinely located
in and feeding the same volume. Both rows stand as written.

**Level identifiers keep the source codes; labels spell them out.** The identifiers stay
`entity:QNL_B` / `_L1` / `_L2` / `_T1`, matching the level segment your room tags carry,
but `rdfs:label_en` reads "Basement", "Level 1", "Level 2", "Terrace 1" — `T1` confirmed
by you as the terrace level. No
`rec:levelNumber` is asserted. `B` is typed `rec:BasementLevel`; the other three are
`rec:Level`.

**Identifiers taken from the source, regularised to one shape.** Every asset carries the
building code in front of its register tag, QF SSC style — SSC subjects read
`entity:SSC_FCU0001`, so QNL reads `entity:QNL_FCU_1F_056` and
`entity:QNL_VAV_B_S11_024`. **Tags are otherwise untouched**; only `QNL_` was added, so
they remain the BMS join key.

The one exception is the AHUB family, at your direction: `AHUB002` becomes
`entity:QNL_AHU_B_002`, so all four families now parse as `TYPE_LEVEL_COUNT`. All 15 are
in the crosswalk, and the 297 VAV and CAV `rec:isFedBy` rows point at the new form. `ref:ifcName` and `rdfs:label_en` carry the same prefixed form,
as SSC does with `SSC_AHUB0001`.

Rooms keep their name text but are rebuilt to a single shape,
`entity:QNL_<level>_<number>_<name>`, because the schedule was not consistent about it.
285 of the 336 rooms already wrote the level and the room number as separate segments
(`QNL_B_034_MEETING_ROOM`); **51 did not** and have been brought into line:

| Source | In the sheet |
|---|---|
| `entity:QNL_B036_REST_REST_ROOM_WOMEN` | `entity:QNL_B_036_REST_REST_ROOM_WOMEN` |
| `entity:QNL_B-ST-01_ST-01` | `entity:QNL_B_ST-01_ST-01` |
| `entity:QNL_L1023_1_CORRIDOR` | `entity:QNL_L1_023_1_CORRIDOR` |
| `entity:QNL_L2-L-1_1_L-1` | `entity:QNL_L2_L-1_1_L-1` |
| `entity:QNL_ST-04_ST-04` | `entity:QNL_B_ST-04_ST-04` |

Only the join between segments changed — no name text, no room number, no disambiguating
tag (`REST`, `COR`, `BOH`) was altered, and no typo was fixed. The other edit anywhere is
stripping the trailing space from `entity:QNL_L2_018_GROUP_STUDY_ROOM_8`, which the
validator rejects outright (`E-WS-1`).

**Only one of the 51 is referenced by your assets sheet** —
`entity:QNL_L1023_2_CORRIDOR`, now `entity:QNL_L1_023_2_CORRIDOR` — so the join to the
register survives almost untouched. All 51 are listed in
`QNL_identifier_crosswalk.csv`, which is where the source→ontology mapping lives.

Seven identifiers had to be invented, because no source supplies them:
`entity:QF`, `entity:QNL`, the four levels `entity:QNL_B` / `_L1` / `_L2`
/ `_T1` (matching the level segment inside your room tags), and `entity:QNL_CHWS-MAIN-LOOP` for
the `CHILLED WATER LOOP` value in the Fed By column.

**The site is `entity:QF`, the same entity QF SSC uses**, not a second name for the
same place — SSC's current sheet writes
`entity:SSC rec:Building rec:isPartOf entity:QF rec:Site`, labelled `SSC Building` and
`Qatar Foundation`. QNL follows exactly: `entity:QNL` labelled `QNL Building`, pointing
at the same `entity:QF`. Sharing the site entity is what lets the two buildings' sheets
join when the converter loads them into one graph; spelling it differently in each would
silently produce two unrelated sites.

**The chilled water loop follows SSC 0.5's shape, with one deliberate departure.** 0.5
writes `entity:CHWS-MAIN-LOOP`, types it `para:Chilled_Water_Loop_Network`, gives it a
`rec:locatedIn` row pointing at the building and an IFC reference, and has terminal units
name it with `rec:isFedBy`. QNL copies all of that.

The departure is the building code. **SSC's loop carries none, yet is
`rec:locatedIn entity:SSC`** — so if QNL reused the bare name, the converter would load
one loop located in two buildings the moment both sheets went into the same graph. Site
level systems like `entity:HVAC` and `entity:QF` are genuinely shared and rightly bare; a
per building main loop is not. QNL therefore writes `entity:QNL_CHWS-MAIN-LOOP`. **If QF
treats this as one shared district loop rather than one per building, say so and I will
drop the prefix** — but then SSC's `rec:locatedIn entity:SSC` row needs revisiting too.

**Labels follow QF SSC, including its dot.** SSC writes `1.001_CORRIDOR` — a dot between
the level and the room number, an underscore before the name. QNL rooms now read
`<level>.<number>_<name>`: `B.063_PLANT_ROOM_01`, `B.237_CORRIDOR`,
`L1.023_1_CORRIDOR`, `B.ST-01_ST-01`. Assets read their raw register tag, `AHUB011`,
`VAV_B_S11_024`, exactly as SSC does with `SSC_FCU0001`.

Label and identifier are built from the same parsed `(level, number, name)` triple, so
they cannot drift apart. No punctuation is stripped and no typo is fixed. This is not the
PARA label rule, which would give `B 063 PLANT ROOM 01`; `E-LBL-1` is therefore switched
off with `--label-style verbatim`, and every other rule stays in force.

`QNL_identifier_crosswalk.csv` lists every source identifier against the identifier used
in the sheet and its label — 336 rooms and 449 assets. 51 room identifiers differ; every
asset identifier is unchanged.

## Classes used

| Source | Class | Basis |
|---|---|---|
| AHUB | `brick:Air_Handling_Unit` | Dar Cairo, 697 rows |
| FCU | `brick:Fan_Coil_Unit` | Dar Cairo, 936 rows |
| VAV | `brick:Variable_Air_Volume_Box` | Brick 1.4 preferred term; no Dar Cairo precedent |
| CAV | `brick:Constant_Air_Volume_Box` | Brick 1.4 preferred term; no Dar Cairo precedent |
| CHILLED WATER LOOP | `para:Chilled_Water_Loop_Network` | Dar Cairo, 127 rows; already in the para registry |

No new `para:` class is proposed. `para:Chilled_Water_Loop_Network` is defined in row 2
of the sheet for readability, but it is an existing registry class, not a new coinage.
1,188 `I-TYP-6` info lines are the VAV and CAV classes — valid Brick 1.4, simply the
first time this house has used them.

## The systems layer

`entity:HVAC` `brick:isPartOf` `entity:QF`, labelled "HVAC System", and all 449 assets
plus the chilled water loop `brick:isPartOf` it. This is what the front end builds its
system tree from — the `brick:isPartOf` chain here, plus Brick's own class hierarchy for
the layer below, since `brick:Air_Handling_Unit` is already declared under
`brick:HVAC_Equipment` in the ontology the viewer loads. No `entity:Air_Handling_Unit`
was minted between the two: neither reference model has one, and it would restate what
Brick already says.

**The loop sits under `entity:CHW-System`.** I said last round that a CHW-System node
would hold only the loop and so would not earn its place. That was wrong on a fact I
should have checked: **QF SSC 0.5 already declares `entity:CHW-System`**, bare and
site-level under `entity:HVAC`, holding its four chilled water booster pumps and five
heat exchangers. QNL is not creating a node — it is joining one that has nine members,
the same way both buildings already share `entity:QF` and `entity:HVAC`. Once the
converter loads both sheets, the group has ten.

Worth flagging back to the SSC side: **SSC leaves its own `entity:CHWS-MAIN-LOOP` outside
`CHW-System`**, attached only by `rec:locatedIn`. A distribution loop is part of the
chilled water system by any reading, so that looks like an oversight rather than a
decision.

**One divergence from house precedent.** Both reference models type the system
`brick:HVAC_System`, which Brick 1.4 lists as an alias. The class ladder says use the
preferred term and `assets/example-minimal.csv` already does, so QNL writes
`brick:Heating_Ventilation_Air_Conditioning_System`. Say the word if you would rather
match the reference models and take the `W-TYP-5` warnings.

## External references — the SSC shape

Each asset carries one `ref:hasExternalReference` row, matching QF SSC's IFC shape:

```
entity:AHUB011 | brick:Air_Handling_Unit | ref:hasExternalReference | <blanknode> |
ref:IFCReference | | | para:IFC_ID | <empty> | | | ref:ifcName | AHUB011
```

`para:IFC_ID` is the slot for the real BIM GUID and is empty, as you asked.
`ref:ifcName` is filled with the entity name, which is derivable and is what both
reference models put there.

**No `ref:TimeseriesReference` rows.** A timeseries reference belongs to a point, not to
the equipment — every one of SSC's 1,767 sits on a `brick:hasPoint` object and none on a
piece of equipment. QNL has no points because no IO list was supplied, so it has no
timeseries references. They arrive with the IO list, on the point rows.

## Validator result

```
python3 validate_ontology.py QNL_Ontology.xlsx --label-style verbatim
2577 rows, 793 typed entities, 1 para: definitions
450 errors, 1 warnings, 1936 advisories
```

**All 450 errors are the same rule, `E-PAIR-1`, and all of them are deliberate** — the
empty `para:IFC_ID` on each of the 449 assets and on the loop. Paste the IFC GUIDs into
`object_prop_val` on those rows and the sheet validates clean.

**The one warning is worth your attention.** `W-REF-1` reports that `entity:QF` is
referenced as an object but never given a row of its own. QF SSC 0.5 does the same — it
declares `entity:SSC` but never `entity:QF` — so as things stand *no* sheet declares the
site. Its label reaches the graph through the object prop on QNL's building row, so
nothing breaks today, but somebody should own a `entity:QF rec:Site` row. Tell me if that
should be QNL and I will add it. Nothing else is outstanding: zero warnings, so every entity is
labelled, every terminal unit has a feeds row and a location, and every spatial entity
connects up to `rec:Building`.

Without `--label-style verbatim` you also get 771 `E-LBL-1` — that is the PARA label
rule objecting to the SSC label style, and it is expected.

## Left out, and why

- **Points, and with them every timeseries reference.** No IO list was supplied, so no
  equipment carries a `brick:hasPoint` row and nothing carries a
  `ref:TimeseriesReference` — the reference hangs off the point, not the equipment.
  Send the IO list and both layers land together. When you do, `check_io_list.py`
  cross-checks the two in both directions so no point ships that the BMS does not
  publish — and passing `--io` to the other two checkers lets them settle the findings
  the list can adjudicate instead of leaving them for someone to work through by hand.
- **Nameplate properties.** No manufacturer datasheets were supplied, so no rated power,
  flow, capacity, model number or manufacturer appears. Nothing is guessed.
- **Zones.** No `rec:Zone` or `rec:HVACZone` layer; no zone data was supplied. Rooms sit
  directly under their level, which satisfies the spatial-connectivity rule. Dar Cairo
  normally interposes a per-floor parent zone — worth adding if the QNL zoning drawings
  turn up.
- **IFC references on rooms.** Requested for equipment only, so rooms have none.
- **Parts.** No `brick:hasPart` breakdown (fans, coils, VFDs) — not requested, and no
  part-level source was supplied.

## The asset register is not internally consistent

You asked me not to change the tags, so nothing below has been changed — this is the
audit, for the register's owner to decide on. All 449 tags are unique.

| Family | Shape | n |
|---|---|---|
| VAV | `VAV_<level>_S<system>_<count>` | 246 |
| CAV | `CAV_<level>_S<system>_<count>` | 51 |
| FCU | `FCU_<level>_<count>` | 137 |
| AHUB | `AHUB<count>` → written `AHU_B_<count>` | 15 |

1. ~~**AHUB is the odd family out.**~~ **Fixed at your direction** — `AHUB011` is now
   `QNL_AHU_B_011`, matching the `TYPE_LEVEL_COUNT` shape of the other three. This is the
   only asset tag that was reshaped. Your BMS still knows these units as `AHUB011`, so
   the crosswalk is the join for them.
2. **FCU has no system segment** where VAV and CAV do. That may be correct — FCUs are fed
   by the chilled water loop, not by an AHU, so there is no `S##` to name — but it means
   the four families cannot be parsed by one rule.
3. **One tag breaks its own family: `VAV_1F_S15_039S`** — a trailing `S` that no other
   tag carries. Either a variant marker that should be a separate segment, or a typo.
4. **Level tokens use a different vocabulary from the rooms.** Assets say `B`, `1F`, `2F`;
   the room schedule and the level entities say `B`, `L1`, `L2`, `T1`. Nothing joins on
   them today, so nothing breaks, but the two vocabularies will need reconciling if a
   query ever tries.

## Things to check in the source data

1. **`ST-04` has no level prefix.** Every other stair is `B-ST-nn` or `L1-ST-nn`. It is
   modelled on level `B` alongside `ST-01`, `ST-02`, `ST-03`, `ST-05`. Confirm.
2. **`entity:QNL_L2_018_GROUP_STUDY_ROOM_8` has a trailing space** in the room list.
   Matched on the stripped value; the space is gone from the ontology identifier.
3. **`T1` has 7 rooms and no equipment** — 2 open terraces and 5 IDF rooms. Confirm
   nothing is missing rather than the level being genuinely unserved.
4. **Typos preserved as instructed** — `SPRIMKLERS_PUMPS_&_ZONES_VALVES`, `DISH_WASING`,
   `ITTIGATION_CONTROL_ROOM`, `CTRCULATION_OFFICE`, `GREEM_ROOM`, `STUDENT_CARRLES`,
   `L1_002A_GREEM_ROOM`. These reach end users through `rdfs:label_en`. Say the word and
   they are a one-line change.
5. **172 rooms carry no equipment.** They are in the sheet because rooms were in scope;
   whether they should have terminal units is a question for the mechanical drawings.

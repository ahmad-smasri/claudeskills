# Ontology Primer for PARA Brick CSV Authoring

A learning document, written from three sources:

- `BrickSchema.md` — the Brick documentation (brickschema.org / docs.brickschema.org)
- `Ontology Webinar.pdf` — notes from the Brick webinar
- `PARA Ontology Workflow Documentation 11.pdf` — the DAR / PARA OS in-house workflow (Rev 0.0, June 2025)

Audience: someone new to ontologies who is responsible for producing the **Excel/CSV of triples**
that the backend and frontend teams convert into `.ttl` files.

---

## Part 1 — The mental model

### 1.1 What problem is being solved

Building data is siloed. Every BMS vendor names its points differently: `AHU2_SAT`,
`ahu-2.supply.temp`, `RTU2_DA_T`. A human can guess what these mean; software cannot. So every
analytics app, every dashboard, every energy model has to be re-wired by hand for every building.
That does not scale.

An **ontology** fixes this by giving every device, space, and data point a *precise, machine-readable
meaning* and by recording *how they are connected*. Once a building is described in Brick, an
application written for one building can run on another without re-mapping.

The webinar notes put it well: Brick is not a replacement for BIM or for physics-based modeling. It
is an **abstraction layer for metadata**. BIM knows the geometry; Brick knows what the thing *is*,
what it's *part of*, what it *feeds*, and *what data it produces*.

### 1.2 RDF, triples, and the graph

Brick is expressed in **RDF** (Resource Description Framework), the W3C standard for representing
information as a graph.

The atom of RDF is the **triple**:

```
Subject  —  Predicate  —  Object
```

Read it as an English sentence:

| Subject | Predicate | Object | Reads as |
|---|---|---|---|
| `entity:Dar-Cairo` | `rec:isPartOf` | `entity:Smart-Village` | "Dar Cairo is part of Smart Village" |
| `entity:AHU-B1-02` | `brick:hasPart` | `entity:AHU-B1-02_SF` | "AHU-B1-02 has a part: its supply fan" |
| `entity:AHU-B1-02_SF` | `brick:hasPoint` | `entity:AHU-B1-02_SF_Speed-Cmd` | "the supply fan has a point: a speed command" |

A **graph** is just a pile of triples. Nodes are entities; edges are predicates. There is no
"top" or "start" — the graph is the sum of all statements.

**This is the single most important idea for your job: one row of your Excel = one triple = one
sentence about the building.** Your whole spreadsheet is one graph.

### 1.3 URIs and namespaces

Every subject, predicate, and object needs a globally unique name. RDF uses **URIs** for this. Full
URIs are long, so we use **prefixes** (a short alias for a URI).

| Prefix | Full URI | What lives here |
|---|---|---|
| `brick:` | `https://brickschema.org/schema/Brick#` | Brick classes (`Air_Handling_Unit`) and relations (`hasPart`, `hasPoint`, `feeds`) |
| `rec:` | `https://w3id.org/rec#` | RealEstateCore — **spatial** classes (`Site`, `Building`, `Level`, `Room`, `Zone`) and relations (`isPartOf`, `locatedIn`, `includes`) |
| `ref:` | `https://brickschema.org/schema/Brick/ref#` | External references (`TimeseriesReference`, `hasTimeseriesId`) |
| `unit:` | `http://qudt.org/vocab/unit/` | QUDT units (`unit:KiloW`, `unit:DEG_C`, `unit:M2`) |
| `qudt:` | `http://qudt.org/schema/qudt/` | QUDT schema itself |
| `rdf:` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | `rdf:type` (the "is a" edge) |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` | `rdfs:label`, `rdfs:subClassOf` |
| `owl:` | `http://www.w3.org/2002/07/owl#` | `owl:Class`, `owl:ObjectProperty` — used when *defining* new classes |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` | Datatypes (`xsd:decimal`, `xsd:boolean`) |
| `bacnet:` | `http://data.ashrae.org/bacnet/` | BACnet object references |
| **`entity:`** | *project-specific* | **Your building's actual things** — instances |
| **`para:`** | *DAR-specific* | **Your custom classes/properties** that Brick doesn't have |

Two of these are yours and matter constantly:

- **`entity:`** — every real thing in *this* building. `entity:AHU-B1-02` is a specific AHU.
- **`para:`** — anything DAR invents. **Never invent a `brick:` or `rec:` term.** If Brick doesn't
  have it, it becomes `para:`. This is a hard rule from the PARA doc.

### 1.4 Class vs. instance — the distinction beginners trip on

- A **class** is a *category*: `brick:Air_Handling_Unit`. It is defined once, in the ontology.
- An **instance** is a *thing*: `entity:AHU-B1-02`. It exists in *your* building.

The edge that connects them is `rdf:type` (written `a` in Turtle shorthand):

```turtle
entity:AHU-B1-02  a  brick:Air_Handling_Unit .
```

In the PARA CSV, you never write `rdf:type` in the `predicate` column. Instead it is captured by the
**`subjectType`** and **`objectType`** columns. That is what those columns *are* — they are `rdf:type`
triples folded into the row so you don't have to write a separate row for them.

So this single CSV row:

| subject | subjectType | predicate | object | objectType |
|---|---|---|---|---|
| `entity:Dar-Cairo` | `rec:Building` | `rec:isPartOf` | `entity:Smart-Village` | `rec:Site` |

is actually **three** triples in TTL:

```turtle
entity:Dar-Cairo    a  rec:Building .
entity:Smart-Village a  rec:Site .
entity:Dar-Cairo    rec:isPartOf  entity:Smart-Village .
```

### 1.5 Where Turtle (`.ttl`) fits

Turtle is just a *file format* for writing triples down. The backend/frontend team converts your CSV
into it. You don't have to write Turtle, but you should be able to **read** it, because it's how you
verify your CSV was interpreted correctly.

Turtle shorthand you'll see:

- `a` = `rdf:type`
- `;` = "same subject, next predicate"
- `,` = "same subject and predicate, next object"
- `.` = end of statement
- `[ ... ]` = a **blank node** (see Part 4)

```turtle
entity:AHU-B1-02  a  brick:Air_Handling_Unit ;
    rec:locatedIn   entity:Dar-Cairo_Basement-1 ;
    brick:hasPart   entity:AHU-B1-02_SF , entity:AHU-B1-02_CHW-Coil ;
    rdfs:label_en   "AHU B1-02" .
```

### 1.6 OWL vs. SHACL (context, not a daily concern)

The webinar notes flag that Brick moved from **OWL** toward **SHACL** (Shapes Constraint Language).
Why it matters conceptually:

- OWL assumes an **open world**: "not stated" means "unknown."
- SHACL supports a **closed world**: "not stated" means "not there" — which is the right assumption
  for concrete, physical building systems.

SHACL lets you write **shapes** = requirements ("a valid VAV must have a damper position command and
a zone air temperature sensor"), then *validate* your graph against them. This gives the webinar's
key idea of **semantic sufficiency**: a model is "complete" not in the abstract, but when it has
enough metadata to run the specific applications you need. Validation tells you what's missing.

You are not writing SHACL. But it explains *why* the reviewers will push back on missing points —
they're checking sufficiency for the PARA OS apps.

---

## Part 2 — The PARA CSV structure

This is the contract between you and the backend team. **Every row is one triple**, plus optional
metadata attached to the subject and/or the object.

### 2.1 The nine core columns

| # | Column | Meaning | Example |
|---|---|---|---|
| 1 | `subject` | The thing you're describing | `entity:Dar-Cairo` |
| 2 | `subjectType` | Its class (`rdf:type`) | `rec:Building` |
| 3 | `predicate` | The relationship or property | `rec:isPartOf` |
| 4 | `object` | What it relates to — an entity, a literal, or `<blanknode>` | `entity:Smart-Village` |
| 5 | `objectType` | The object's class, if the object is an entity | `rec:Site` |
| 6 | `subject_prop_name` | *(optional)* a metadata property **about the subject** | `rdfs:label_en` |
| 7 | `subject_prop_val` | *(optional)* its value | `Dar Cairo` |
| 8 | `object_prop_name` | *(optional)* a metadata property **about the object** | `brick:hasUnit` |
| 9 | `object_prop_val` | *(optional)* its value | `unit:KiloW` |

### 2.2 Rules that follow from that

1. **The `_prop_` columns repeat.** You may add more `object_prop_name` / `object_prop_val` pairs
   (and subject pairs) side by side in the same row to attach as many attributes as needed. A row
   carrying a value *and* a unit uses two object-prop pairs.
2. **Leave cells blank when they don't apply.** If you're only describing the object (e.g. giving a
   unit), leave `subject_prop_name` / `subject_prop_val` empty.
3. **`subject_prop_*` describes the subject; `object_prop_*` describes the object.** Getting these
   backwards is the most common mistake — e.g. putting a point's label in `subject_prop_val` when
   the point is the *object* of a `brick:hasPoint` row.
4. **Type columns can be omitted on repeat mentions**, but be consistent: declare a type at least
   once, and don't declare *conflicting* types for the same entity.
5. **`rdfs:label_en` is what the front end displays.** This is the only place spaces are allowed.
   Every entity a user will see needs one.

### 2.3 Anatomy of the four row shapes

Almost every row you write is one of four shapes. Learn these and you can write the whole file.

**Shape A — Relationship between two entities**

| subject | subjectType | predicate | object | objectType | subject_prop_name | subject_prop_val |
|---|---|---|---|---|---|---|
| `entity:Zone-A` | `rec:Zone` | `rec:isPartOf` | `entity:Dar-Cairo` | `rec:Building` | `rdfs:label_en` | `Zone-A` |

```turtle
entity:Zone-A  a rec:Zone ; rdfs:label_en "Zone-A" ; rec:isPartOf entity:Dar-Cairo .
entity:Dar-Cairo a rec:Building .
```

**Shape B — Attaching a data point**

| subject | subjectType | predicate | object | objectType | object_prop_name | object_prop_val | object_prop_name | object_prop_val |
|---|---|---|---|---|---|---|---|---|
| `entity:Dar-Cairo_Electrical-Virtual-Meter` | `brick:Electrical_Meter` | `brick:hasPoint` | `entity:Dar-Cairo_Electrical-Virtual-Meter_Avg-Elec-Demand` | `brick:Electric_Power_Sensor` | `rdfs:label_en` | `Dar Cairo Avg Electricity Demand` | `brick:hasUnit` | `unit:KiloW` |

Note the label and unit are **object** props — they describe the point, and the point is the object.

**Shape C — A property with a value and a unit (blank node)**

| subject | subjectType | predicate | object | objectType | object_prop_name | object_prop_val | object_prop_name | object_prop_val |
|---|---|---|---|---|---|---|---|---|
| `entity:AHU-B1-01_SF_Motor` | `brick:Motor` | `brick:ratedPowerInput` | `<blanknode>` | `<blanknode>` | `brick:value` | `5.5` | `brick:hasUnit` | `unit:KiloW` |

```turtle
entity:AHU-B1-01_SF_Motor  a brick:Motor ;
    brick:ratedPowerInput [ brick:value 5.5 ; brick:hasUnit unit:KiloW ] .
```

**Shape D — Defining a new class (extension)**

| subject | subjectType | predicate | object | subject_prop_name | subject_prop_val |
|---|---|---|---|---|---|
| `para:Pressure_Independent_Module` | `owl:Class` | `rdfs:subClassOf` | `brick:Terminal_Unit` | `rdfs:label_en` | `Pressure Independent Module` |

Note `subject` here is a **class**, not an `entity:` — this is the one shape where that's true.

---

## Part 3 — Naming conventions (PARA / BIM)

These come straight from the PARA doc and they are non-negotiable, because the `IFC_ID` links your
ontology to the BIM model and the 3D viewer.

| Level | Pattern | Example |
|---|---|---|
| Site | `Site-Name` | `Smart-Village` |
| Building | `Building-Name` | `Dar-Cairo`, `150H` |
| Floor / Level | `Building-Name_Floor-XX` | `150H_Floor-7` |
| Room | `Building-Name_Floor-XX_Room-Name_Number` | `150H_Floor-7_Office_567` |
| HVAC Zone | `Building-Name_Floor-XX_HVAC-Zone` | `Dar-Cairo_Floor-1HC-H1` |
| Parent Zone | `Building-Name_Floor-XX_Parent-Zone` | `Zone-A` |
| Equipment | `<Equipment-Type>_<Floor-Number>_<Unique-ID or Count>` | `AHU-B1-02`, `CHWP-B1-1-PUMP-7-LEFT` |
| Equipment part | `Equipment-Name-Number_Part-Name` | `AHU-B1-02_SF` |
| Point | `Equipment-Name-Number_Part-Name_Point-Name` | `AHU-B1-02_SF_VFD_Elec-Demand` |
| `IFC_ID` | Same as subject name **without** `entity:` and without spaces | `Dar-Cairo_Floor-7_Office_567` |

**Containment rules:** Room `isPartOf` HVAC Zone; HVAC Zone `isPartOf` Parent Zone.

**A Parent Zone is not an HVAC Zone.** A Parent Zone is a geometric/wayfinding grouping of adjacent
rooms. An HVAC Zone (per ASHRAE) is a space or group of spaces served by one HVAC system or portion
of one, with controlled temperature/humidity/ventilation.

### Character rules

- **Dashes (`-`) separate words** inside one segment: `Dar-Cairo`, not `dar cairo` or `darCairo`.
- **Underscores (`_`) separate segments** of an identifier: `Dar-Cairo_Basement-3_Pump-Room_B331`.
- **No spaces anywhere**, ever — except inside an `rdfs:label_en` *value*.
- **Case is significant.** `rec:Building` ≠ `rec:building` ≠ `Rec:Building`. Brick class names use
  `Title_Case_With_Underscores`; properties use `camelCase`.
- **Abbreviations only if industry-standard**: AHU, FCU, VAV, CRAC, CHWP, VFD.

Worked breakdowns from the doc:

- `CHWP-B1-1-PUMP-7-LEFT` → type `CHWP` (chilled water booster pump) + floor `B1-1` (basement 1) +
  unique ID `PUMP-7-LEFT`
- `AHU-B1-02` → type `AHU` + floor `B1` + count `02` (second unit on that floor)

---

## Part 4 — Relationships: which one, when

This is where modeling judgment lives. Brick's own guidance, plus how PARA applies it.

### 4.1 The four families

| Family | Question it answers | Predicates |
|---|---|---|
| **Composition** | What is this made of? | `brick:hasPart` / `rec:isPartOf` |
| **Topology** | Where is it, what's upstream/downstream? | `rec:locatedIn`, `brick:feeds` |
| **Telemetry** | What data does it produce? | `brick:hasPoint` / `brick:isPointOf` |
| **Control** | Who controls / hosts what? | `brick:controls`, `brick:hosts` (Brick 1.5) |

### 4.2 Cheat sheet — when your subject is a…

- **Location** → `hasPart` gives its components: Floor `hasPart` Room; HVAC Zone `hasPart` Room
- **Point** → `isPointOf` gives what the data is about: Sensor `isPointOf` Room
- **Equipment** →
  - `hasPoint` for its telemetry: VAV `hasPoint` Temperature Sensor
  - `hasLocation` / `rec:locatedIn` for where it physically sits: Thermostat `locatedIn` Room
  - `hasPart` for its components: AHU `hasPart` Supply Fan
  - `feeds` for downstream: AHU `feeds` VAV; VAV `feeds` HVAC Zone
  - `isControlledBy` for its controller
- **ICT Equipment** → `hosts` for points it exposes: BACnet_Device `hosts` Temperature_Sensor
- **Controller** → `controls`: VAV_Controller `controls` VAV

### 4.3 `hasPart` vs `locatedIn` — the classic confusion

Brick's own test: **is the containment fundamental to the identity of the container?**

- A chair in a room → `locatedIn`. A room is still a room without the chair.
- A damper in a VAV → `hasPart`. A VAV is *not* a VAV without something to modulate airflow.

### 4.4 Inverse relationships

Every relationship can be stated in either direction. `A hasPoint B` and `B isPointOf A` are the
same fact. Pick a direction and be consistent across the file — mixing directions makes the sheet
hard to review even though the graph is identical.

| Relationship | Inverse |
|---|---|
| `hasPoint` | `isPointOf` |
| `hasPart` | `isPartOf` |
| `hasLocation` | `isLocationOf` |
| `feeds` | `isFedBy` |
| `controls` | `isControlledBy` |
| `hosts` | `isHostedBy` |

### 4.5 Why PARA uses `rec:` for spatial things

As of Brick 1.4, **all Brick `Location` classes are deprecated** in favor of RealEstateCore. Using
`brick:Building` now raises a validation warning and Brick's own SHACL rules will rewrite it to
`rec:Building`.

| Brick (deprecated for spatial) | Use instead |
|---|---|
| `brick:Building` | `rec:Building` |
| `brick:Floor` | `rec:Level` |
| `brick:Room` | `rec:Room` |
| `brick:hasLocation` | `rec:locatedIn` |
| `brick:isPartOf` | `rec:isPartOf` |
| `brick:Collection` (v1.5) | `rec:Collection`, membership via `rec:includes` |

**Practical rule for the PARA sheet:**

- **Spatial hierarchy** (site → building → level → zone → room) → `rec:` classes, `rec:isPartOf` /
  `rec:locatedIn`
- **Equipment, parts, points** → `brick:` classes, `brick:hasPart` / `brick:hasPoint`
- **Custom anything** → `para:`

---

## Part 5 — Properties, blank nodes, and data points

### 5.1 Entity properties and the blank-node pattern

A property that has both a **value** and a **unit** cannot be a plain literal — a literal can't carry
a unit. So Brick wraps it in an intermediate node that holds both. In the CSV this is written as
`<blanknode>` in the `object` and `objectType` columns.

Think of `<blanknode>` as **an unnamed box holding related attributes** — like a small struct or a
dict, with no ID of its own because nothing else needs to point at it.

| subject | subjectType | predicate | object | objectType | object_prop_name | object_prop_val | object_prop_name | object_prop_val |
|---|---|---|---|---|---|---|---|---|
| `entity:AHU-TYP2-F3_SF_Fan_VFD` | `brick:Fan_VFD` | `brick:ratedPowerInput` | `<blanknode>` | `<blanknode>` | `brick:value` | `18.5` | `brick:hasUnit` | `unit:KiloW` |
| `entity:AHU-TYP2-F3_SF_Fan_VFD` | `brick:Fan_VFD` | `brick:electricalPhaseCount` | `<blanknode>` | `<blanknode>` | `brick:value` | `3` | `brick:hasUnit` | `unit:UNITLESS` |
| `entity:AHU-TYP2-F3_SF_Fan_VFD` | `brick:Fan_VFD` | `brick:ratedVoltageInput` | `<blanknode>` | `<blanknode>` | `brick:value` | `380` | `brick:hasUnit` | `unit:V` |
| `entity:AHU-TYP2-F3_CHW-Coil` | `brick:Chilled_Water_Coil` | `brick:coolingCapacity` | `<blanknode>` | `<blanknode>` | `brick:value` | `159` | `brick:hasUnit` | `unit:KiloW` |
| `entity:AHU-TYP2-F3_CHW-Coil` | `brick:Chilled_Water_Coil` | `para:ratedChilledWaterFlowrate` | `<blanknode>` | `<blanknode>` | `brick:value` | `5.44` | `brick:hasUnit` | `unit:L-PER-SEC` |

```turtle
entity:AHU-TYP2-F3_SF_Fan_VFD  a brick:Fan_VFD ;
    brick:ratedPowerInput      [ brick:value 18.5 ; brick:hasUnit unit:KiloW ] ;
    brick:electricalPhaseCount [ brick:value 3    ; brick:hasUnit unit:UNITLESS ] .
```

Notice the last row: `para:ratedChilledWaterFlowrate` — Brick has no such property, so it gets the
`para:` prefix.

**Properties vs. data points.** Both use blank nodes, and beginners confuse them:

- A **property** is a static nameplate fact — rated power, cooling capacity, gross area. It doesn't
  change. It has no timeseries.
- A **data point** is a live/measured/calculated value — a sensor, setpoint, command, alarm, status.
  It *does* have a timeseries and gets an external reference.

### 5.2 Units — always from QUDT

Units are QUDT instances, attached with `brick:hasUnit`. Pick from
<https://ontology.brickschema.org/qudt/Unit.html>.

Common ones: `unit:KiloW`, `unit:KiloW-HR`, `unit:DEG_C`, `unit:DEG_F`, `unit:M2`, `unit:V`,
`unit:A`, `unit:L-PER-SEC`, `unit:PPM`, `unit:PERCENT`, `unit:UNITLESS`.

Where QUDT genuinely has no unit — tariffs, emission factors, degree-days — PARA mints its own under
`para:`, e.g. `para:EGP-PER-KiloW-HR`, `para:USD-PER-EGP`, `para:KiloGM-CO2-PER-KiloW-HR`,
`para:CDD_DEGC_CALC`. Check whether one already exists before inventing another.

**Use `unit:UNITLESS` rather than leaving the unit blank** for dimensionless quantities like COP,
phase count, or a working-day flag.

### 5.3 Modeling a data point — the four steps

**Step 1 — Identify the parent.** Every point hangs off an equipment or meter.

**Step 2 — Define the point** with `brick:hasPoint`, typed as a Brick Point class
(`brick:Electric_Power_Sensor`, `brick:Zone_Air_Temperature_Sensor`, …).

**Step 3 — Add metadata**: `rdfs:label_en` (front-end name) and `brick:hasUnit`. Both are mandatory
for anything quantifiable.

**Step 4 — Link to the external timeseries:**

| subject | subjectType | predicate | object | objectType | object_prop_name | object_prop_val | object_prop_name | object_prop_val |
|---|---|---|---|---|---|---|---|---|
| `entity:Dar-Cairo_Electrical-Virtual-Meter_Total-Elec-Demand` | `brick:Electric_Power_Sensor` | `ref:hasExternalReference` | `<blanknode>` | `ref:TimeseriesReference` | `ref:hasTimeseriesId` | `ELEC_KW_CALC` | `para:hasEntityId` | `Smart Village` |

- `ref:hasTimeseriesId` — the telemetry key in the external timeseries DB
- `para:hasEntityId` — DAR's custom property identifying the device that owns that telemetry in the
  external system

Note the `objectType` here is **`ref:TimeseriesReference`**, not `<blanknode>` — the node is
anonymous but it *is* typed. Compare with the value/unit blank nodes, which are untyped.

### 5.4 Virtual meters

A **virtual meter** is a formula standing in for hardware you don't have — e.g. "Building Electricity
Demand = sum of each floor's electrical demand," recalculated on an interval. Brick models it as a
normal meter class with `brick:isVirtualMeter [ brick:value true ]`. PARA's examples use
`brick:Electrical_Meter` with a `-Virtual-Meter` naming convention.

Meters relate to each other **only** via `brick:hasSubMeter` / `brick:isSubMeterOf`, and to what they
measure via `brick:meters` / `brick:isMeteredBy`.

### 5.5 Aggregations

An aggregation summarizes many timeseries readings into one value.

| subject | subjectType | predicate | object | objectType | object_prop_name | object_prop_val |
|---|---|---|---|---|---|---|
| `entity:Dar-Cairo_Electrical-Virtual-Meter_Avg-Elec-Demand` | `brick:Electric_Power_Sensor` | `brick:aggregate` | `<blanknode>` | `<blanknode>` | `brick:aggregationFunction` | `mean` |

Brick also defines `brick:aggregationInterval` using ISO 8601 repeating durations: `RPT1H` (hourly),
`RPT15M` (15 min), `RPT2H`, `RP1M` (monthly), `RP30D`.

**Key rule from the PARA doc:** if the aggregation has a *different* TimeseriesId in the external DB
than the raw point, it must be modeled as a **separate data point** — same class, its own name, its
own external reference. That's why you see both `_Total-Elec-Demand` and `_Avg-Elec-Demand`.

---

## Part 6 — Extending Brick

Brick is deliberately extensible. When a component doesn't exist in Brick, you define a subclass.

**Rules:**

1. Namespace it `para:` — never `brick:` or `rec:`.
2. Type it `owl:Class` (in `subjectType`).
3. Give it a correct parent with `rdfs:subClassOf` — this is what makes it inherit the parent's
   properties and makes it discoverable to applications. Pick the *most specific* correct parent.
4. Give it an `rdfs:label_en` and, ideally, a `skos:definition`.
5. **All new subclasses live in one shared PARA `.ttl` file** that is imported by every project
   ontology — not scattered in project files.
6. **New subclasses are reviewed before being added**, to avoid redundancy and wrong definitions.

Example from the doc — a Pressure Independent Module:

| subject | subjectType | predicate | object | subject_prop_name | subject_prop_val |
|---|---|---|---|---|---|
| `para:Pressure_Independent_Module` | `owl:Class` | `rdfs:subClassOf` | `brick:Terminal_Unit` | `rdfs:label_en` | `Pressure Independent Module` |

```turtle
para:Pressure_Independent_Module  a owl:Class ;
    rdfs:subClassOf brick:Terminal_Unit ;
    rdfs:label_en   "Pressure Independent Module" .
```

New **properties** follow the same pattern but use `owl:ObjectProperty` (value is another entity) or
`owl:DatatypeProperty` (value is a number/string), with `rdfs:subPropertyOf` pointing at the Brick
relation being specialized, plus `rdfs:domain` / `rdfs:range`.

**Before extending, search Brick.** Use <https://ontology.brickschema.org> — it has far more classes
than people expect. Also beware **aliases**: Brick keeps `brick:AHU`, `brick:Air_Handler_Unit`, and
`brick:Air_Handling_Unit` for backwards compatibility, but only one is *preferred*
(`brick:Air_Handling_Unit`); non-preferred ones carry `brick:aliasOf`. Always use the preferred class.

---

## Part 7 — Worked micro-example, end to end

A tiny slice: one site, one building, one floor, one AHU with a supply fan that has a VFD with a
meter and a demand point.

| subject | subjectType | predicate | object | objectType | subject_prop_name | subject_prop_val | object_prop_name | object_prop_val | object_prop_name | object_prop_val |
|---|---|---|---|---|---|---|---|---|---|---|
| `entity:Smart-Village` | `rec:Site` | `brick:hasPart` | `entity:Dar-Cairo` | `rec:Building` | `rdfs:label_en` | `Smart Village` | `rdfs:label_en` | `Dar Cairo` | | |
| `entity:Dar-Cairo_Floor-1` | `rec:Level` | `rec:isPartOf` | `entity:Dar-Cairo` | `rec:Building` | `rdfs:label_en` | `Floor 1` | | | | |
| `entity:AHU-01-01` | `brick:Air_Handling_Unit` | `rec:locatedIn` | `entity:Dar-Cairo_Floor-1` | `rec:Level` | `rdfs:label_en` | `AHU 01-01` | | | | |
| `entity:AHU-01-01` | `brick:Air_Handling_Unit` | `brick:hasPart` | `entity:AHU-01-01_SF` | `brick:Supply_Fan` | | | `rdfs:label_en` | `Supply Fan` | | |
| `entity:AHU-01-01_SF` | `brick:Supply_Fan` | `brick:hasPart` | `entity:AHU-01-01_SF_VFD` | `brick:Fan_VFD` | | | `rdfs:label_en` | `Supply Fan VFD` | | |
| `entity:AHU-01-01_SF_VFD` | `brick:Fan_VFD` | `brick:ratedPowerInput` | `<blanknode>` | `<blanknode>` | | | `brick:value` | `18.5` | `brick:hasUnit` | `unit:KiloW` |
| `entity:AHU-01-01_SF_VFD` | `brick:Fan_VFD` | `brick:hasPart` | `entity:AHU-01-01_SF_VFD_Elec-Meter` | `brick:Electrical_Meter` | | | `rdfs:label_en` | `VFD Electrical Meter` | | |
| `entity:AHU-01-01_SF_VFD_Elec-Meter` | `brick:Electrical_Meter` | `brick:hasPoint` | `entity:AHU-01-01_SF_VFD_Elec-Demand` | `brick:Electric_Power_Sensor` | | | `rdfs:label_en` | `VFD Electrical Demand` | `brick:hasUnit` | `unit:KiloW` |
| `entity:AHU-01-01_SF_VFD_Elec-Demand` | `brick:Electric_Power_Sensor` | `ref:hasExternalReference` | `<blanknode>` | `ref:TimeseriesReference` | | | `ref:hasTimeseriesId` | `AHU0101_SF_VFD_KW` | `para:hasEntityId` | `Dar-Cairo` |

Which becomes:

```turtle
entity:Smart-Village  a rec:Site ; rdfs:label_en "Smart Village" ;
    brick:hasPart entity:Dar-Cairo .

entity:Dar-Cairo  a rec:Building ; rdfs:label_en "Dar Cairo" .

entity:Dar-Cairo_Floor-1  a rec:Level ; rdfs:label_en "Floor 1" ;
    rec:isPartOf entity:Dar-Cairo .

entity:AHU-01-01  a brick:Air_Handling_Unit ; rdfs:label_en "AHU 01-01" ;
    rec:locatedIn entity:Dar-Cairo_Floor-1 ;
    brick:hasPart entity:AHU-01-01_SF .

entity:AHU-01-01_SF  a brick:Supply_Fan ; rdfs:label_en "Supply Fan" ;
    brick:hasPart entity:AHU-01-01_SF_VFD .

entity:AHU-01-01_SF_VFD  a brick:Fan_VFD ; rdfs:label_en "Supply Fan VFD" ;
    brick:ratedPowerInput [ brick:value 18.5 ; brick:hasUnit unit:KiloW ] ;
    brick:hasPart entity:AHU-01-01_SF_VFD_Elec-Meter .

entity:AHU-01-01_SF_VFD_Elec-Meter  a brick:Electrical_Meter ;
    rdfs:label_en "VFD Electrical Meter" ;
    brick:hasPoint entity:AHU-01-01_SF_VFD_Elec-Demand .

entity:AHU-01-01_SF_VFD_Elec-Demand  a brick:Electric_Power_Sensor ;
    rdfs:label_en "VFD Electrical Demand" ;
    brick:hasUnit unit:KiloW ;
    ref:hasExternalReference [
        a ref:TimeseriesReference ;
        ref:hasTimeseriesId "AHU0101_SF_VFD_KW" ;
        para:hasEntityId "Dar-Cairo" ] .
```

Trace the chain: **Site → Building → Level → AHU → Fan → VFD → Meter → Point → Timeseries.** That
spine is the shape of the whole deliverable.

---

## Part 8 — Suggested authoring workflow

1. **Spatial skeleton first.** Site → Buildings → Levels → Parent Zones → HVAC Zones → Rooms. Do the
   whole hierarchy before touching equipment. Every spatial entity gets an `rdfs:label_en` and an
   `IFC_ID`.
2. **Systems.** Declare the systems (HVAC, Electrical, …) that equipment will belong to.
3. **Equipment.** Each asset: type it, locate it (`rec:locatedIn`), attach it to its system
   (`rec:isPartOf`), add nameplate properties from the catalogue.
4. **Parts.** Decompose equipment with `brick:hasPart` down to the level where points attach.
5. **Points.** For each part that produces data: `brick:hasPoint` + class + `rdfs:label_en` +
   `brick:hasUnit`.
6. **External references.** Attach `ref:hasExternalReference` with the timeseries ID once the
   integration team gives you the telemetry names.
7. **Aggregations.** Add derived points where a separate TimeseriesId exists.
8. **Extensions last.** Collect everything Brick couldn't express, propose it as `para:` subclasses,
   submit for review.

Work **one sheet section at a time** and keep sections in the doc's order (Site → Building → Zones →
Equipment → Properties → Points). It makes review tractable.

---

## Part 9 — Review checklist

Run this before handing off.

**Syntax**
- [ ] Every non-empty row has, at minimum, `subject`, `predicate`, `object`
- [ ] Every prefix is one of: `entity:`, `brick:`, `rec:`, `ref:`, `unit:`, `qudt:`, `rdf:`, `rdfs:`, `owl:`, `xsd:`, `bacnet:`, `para:`
- [ ] No spaces in any entity name, class name, or property name
- [ ] Spaces appear **only** inside `rdfs:label_en` values
- [ ] Dashes within segments, underscores between segments
- [ ] Exact case on all Brick/REC terms

**Semantics**
- [ ] Every class used actually exists in Brick/REC — verified on ontology.brickschema.org
- [ ] Preferred class used, not an alias (`Air_Handling_Unit`, not `AHU`)
- [ ] Spatial things use `rec:`, not deprecated `brick:Building` / `brick:Floor` / `brick:Room`
- [ ] Every custom term is `para:`-prefixed and on the extension list for review
- [ ] Each entity has exactly one consistent type everywhere it appears
- [ ] `hasPart` vs `locatedIn` chosen by the "is it fundamental to identity?" test
- [ ] Relationship direction consistent across the file

**Completeness**
- [ ] Every entity shown in the UI has an `rdfs:label_en`
- [ ] Every entity shown in the 3D/BIM view has an `IFC_ID`
- [ ] Every quantitative point and property has a `brick:hasUnit` (use `unit:UNITLESS` if dimensionless)
- [ ] Every unit is a real QUDT unit, or a reviewed `para:` unit
- [ ] Every live data point has a `ref:hasExternalReference` with a `ref:hasTimeseriesId`
- [ ] Every aggregation with its own telemetry name is a separate point
- [ ] Spatial hierarchy is unbroken — no orphan rooms, zones, or floors
- [ ] Every piece of equipment traces up to a location **and** a system

**Prop-column sanity**
- [ ] `subject_prop_*` describes the subject; `object_prop_*` describes the object
- [ ] `<blanknode>` rows carry their `brick:value` / `brick:hasUnit` in **object** prop columns
- [ ] Typed blank nodes (`ref:TimeseriesReference`) have the type in `objectType`, not `<blanknode>`

---

## Part 10 — Open questions to confirm with the PARA team

Points where the Rev 0.0 document is ambiguous or self-inconsistent. Worth resolving before
authoring at volume.

1. **Custom-class prefix.** Chapter Two's CSV uses `para:Pressure_Independent_Module`, but the
   surrounding prose describes the resulting TTL as `brick:PIM`. The `para:` form matches the
   explicit rule in Chapter One Remark 3, so `para:` is almost certainly correct — but confirm.
2. **PIM's parent class.** The prose says it goes under `HVAC_Equipment`; the CSV row says
   `brick:Terminal_Unit`. These are different levels of the hierarchy.
3. **Equipment location typing.** The Chapter One equipment example has
   `rec:locatedIn entity:Dar-Cairo_Basement-1` with `objectType` = `rec:Room`, but `Basement-1` is a
   level, which should be `rec:Level`. Confirm the intended convention for equipment sitting on a
   floor rather than in a room.
4. **Exact column count and header spelling** in the actual template, including how many repeated
   `object_prop_name`/`object_prop_val` pairs the parser accepts.
5. **`rdfs:label_en` vs `rdfs:label`.** `label_en` is not standard RDFS — standard practice is
   `rdfs:label "text"@en`. Confirm the converter handles `label_en` as written.
6. **Brick version target** — 1.4 or 1.5? It changes availability of `brick:controls`,
   `brick:hosts`, `brick:Point_Collection`, and `brick:Automation_Collection`.
7. **The current `para:` extension `.ttl`** — where it lives, and who approves additions.

---

## Glossary

| Term | Meaning |
|---|---|
| **Ontology** | A shared, machine-readable vocabulary + relationships for a domain |
| **RDF** | W3C data model representing information as triples forming a graph |
| **Triple** | Subject–Predicate–Object; one fact; one CSV row |
| **URI** | Globally unique name for a resource |
| **Namespace / prefix** | Short alias for a URI prefix (`brick:` = `https://brickschema.org/schema/Brick#`) |
| **Turtle / TTL** | Human-readable text format for RDF; the deliverable format |
| **Class** | A category (`brick:Air_Handling_Unit`) |
| **Instance / entity** | A specific thing (`entity:AHU-B1-02`) |
| **`rdf:type`** | The "is a" edge from instance to class; the `subjectType`/`objectType` columns |
| **Blank node** | Anonymous intermediate node grouping related attributes (value + unit) |
| **Point** | A data source or sink: Sensor, Setpoint, Command, Alarm, Status, Parameter |
| **Entity property** | Static attribute of an entity (rated power, area) — not a timeseries |
| **QUDT** | The units ontology Brick uses |
| **Virtual meter** | A computed meter with no physical hardware |
| **Aggregation** | A summarized timeseries (mean/max over an interval) |
| **External reference** | Link from a Brick Point to its ID in an external timeseries/BACnet system |
| **SHACL** | Constraint language used to validate that a model is complete for an application |
| **Semantic sufficiency** | The model has enough metadata to run the required applications |
| **BuildingMOTIF** | Open-source SDK for template-based Brick model creation + SHACL validation |
| **REC** | RealEstateCore — the ontology Brick now defers to for spatial classes |

---

## Reference links

- Brick class explorer — <https://ontology.brickschema.org>
- QUDT units list — <https://ontology.brickschema.org/qudt/Unit.html>
- Brick developer docs — <https://docs.brickschema.org>
- `brickschema` Python package — <https://brickschema.readthedocs.io>
- ref-schema (external references) — <https://github.com/gtfierro/ref-schema>
- RealEstateCore — <https://w3id.org/rec>
- YASGUI (SPARQL query GUI, for checking a graph) — <https://yasgui.triply.cc>
- Source webinar — <https://www.youtube.com/watch?v=J9wYIou6LWQ>

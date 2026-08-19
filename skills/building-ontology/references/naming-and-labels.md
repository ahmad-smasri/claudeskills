# Naming and labels

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
`clean_label()` in that script is the reference implementation.

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

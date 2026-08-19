# claudeskills

Claude Code skills.

## `skills/building-ontology`

Authoring skill for PARA/Brick building ontology spreadsheets - the 9-column
sheet of RDF triples that the backend converts to `.ttl`.

It carries the naming and modelling rules, the class-resolution ladder (Dar Cairo
first, then Brick, then a `para:` subclass), an intake checklist for what to
request when inputs are missing, a lookup tool for finding precedent in the
reference models, and a validator with 30 rule codes.

```
python3 skills/building-ontology/scripts/lookup_reference.py --template brick:Fan_Coil_Unit
python3 skills/building-ontology/scripts/validate_ontology.py MyBuilding.xlsx
skills/building-ontology/tests/run_tests.sh
```

## `reference-models/`

- `DarCairo_V93.csv` - the primary reference for any ontology we build
- `QF_SSC_Ontology_draft0.4.xlsx` - a recent sample, with known defects
- `Ontology_headers.xlsx` - the nine canonical column names

## Source documents

`PARA Ontology Workflow Documentation 11.pdf` (Rev 0.0), `Ontology Webinar.pdf`,
`BrickSchema.md`, and `ontologyprimer.md` - a primer distilled from the three.

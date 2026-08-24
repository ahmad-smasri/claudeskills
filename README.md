# claudeskills

Claude Code skills. **Start with `CLAUDE.md`** - it maps every file here and
states the rules that are already settled, so a session does not have to re-read
the source documents.

## `skills/building-ontology`

Authoring skill for PARA/Brick building ontology spreadsheets - the 9-column
sheet of RDF triples that the backend converts to `.ttl`.

It carries the scope and modelling rules, the class-resolution ladder (Dar Cairo
first, then Brick, then a `para:` subclass, and ask before rooting orphan
equipment), an intake checklist covering the eight inputs to request - including
IO lists for points and manufacturer datasheets for nameplate properties - a
lookup tool for finding precedent in the reference models, and a validator with
30 rule codes.

```
python3 skills/building-ontology/scripts/lookup_reference.py --template brick:Fan_Coil_Unit
python3 skills/building-ontology/scripts/validate_ontology.py MyBuilding.xlsx
skills/building-ontology/tests/run_tests.sh
```

## `reference-models/`

- `DarCairo_V93.csv` - the primary reference for any ontology we build
- `QF_SSC_Ontology_ver02.xlsx` - the cleaned SSC delivery, the step-3 previous-project reference
- `Ontology_headers.xlsx` - the nine canonical column names

## Source documents

`PARA Ontology Workflow Documentation 11.pdf` (Rev 0.0), `Ontology Webinar.pdf`,
`BrickSchema.md`, and `ontologyprimer.md` - a primer distilled from the three.

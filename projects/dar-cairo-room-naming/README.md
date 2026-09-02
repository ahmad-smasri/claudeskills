# Dar Cairo-shaped room subjects for SSC and HQ

One workbook out, one sheet per building, derived from the BMS room-allocation
registers by `build_room_names.py`.

```
python3 build_room_names.py --src SSC=sources/SSC_rooms.xlsx \
    --out SSC_HQ_Room_Names.xlsx --rooms-csv SSC_rooms_distinct.csv
```

SSC is done: 124 asset rows, 69 distinct rooms, 1 unresolved. HQ drops in as a
second `--src` when its workbook arrives, and the output gains an `HQ` sheet.

## The shape

Building, then the room reference, then the name - three segments:

```
entity:SSC_01-014_Shell-Space
entity:SSC_B-016_Sprinkler-And-Water
entity:SSC_01-ST-4_Stair-4
```

The reference segment already carries the level (`01-014`, `B-016`), so a
separate level segment would only repeat it. Dar Cairo likewise ends up with the
level inside its number (`B331`); it just orders the segments the other way,
`entity:Dar-Cairo_Basement-3_Pump-Room_B331`.

Dashes separate words inside a segment, underscores separate segments, and
nothing else survives into a name: `VISITOR'S CUBICLE` -> `Visitors-Cubicle`,
`SPRINKLER & WATER` -> `Sprinkler-And-Water` (Dar Cairo spells the ampersand out
in `Boiler-And-Heat-Exchange`), `ASSOC. DIR. OFFICE` -> `Assoc-Directors-Office`,
`MAIN SEC. CONTROL ROOM` -> `Main-Sec-Control-Room`. Ordinary words are title
case; the tokens in `ACRONYMS` stay upper - `AV-Room`, `IDF-1`,
`IT-Managers-Office`. The dot in the reference becomes a dash, so `01.014` is
the segment `01-014`.

The building code is `SSC`, not the Dar Cairo-style long form. The four level
entities the delivered SSC ontology already ships - `entity:SSC_Level-01`
through `entity:SSC_Level-B1` - are unchanged and are what these rooms hang off
with `rec:isPartOf`; the level no longer appears in the room subject itself.
One thing to note: the basement reference reads `B` where the level entity reads
`B1`, because `B.013` is what the drawings print.

## Which column the name comes from

In source-column order: **D** room name as per drawings, **E** the existing
ontology name, **H** room per the VAV/FCU list, **J** room per the BMS screen.

1. **Green row** - the BMS screen overruled the drawings, which is why the row
   was traced in the first place. Take the last of D, H, J that carries a name;
   on every green SSC row that is J. E is not consulted, because green means E
   is what turned out to be wrong. Where the screen names the room but not its
   number (`ST-4 STAIR 4`), the number still comes from E - only the name was
   in dispute.
2. **Otherwise, D or J on whether H carries a room number** - H carries one, D
   stands; H does not and J has both a number and a name, J stands; no usable
   J, D stands.
3. **E arbitrates the name.** If the picked column disagrees with E and D
   agrees with E, D wins - this is what keeps `ROOM NO 42`, `43` and `44` apart
   from the `SHELL SPACE` they all sit inside, where the screen prints
   `01.029 SHELL SPACE` for all four. If neither agrees with E, the name comes
   from E, which is what corrects the screen's `VISITORS CUBIDE` and
   `RESEARCHER OFFICE`.
4. **One reference, one spelling.** After the row pass, room references
   carrying two spellings of the same name are collapsed onto the fuller one -
   `ASSOC.DIR OFFICE` and `ASSOC. DIRECTORS OFFICE` are one room. Only
   abbreviation variants collapse (token-prefix match); `01.029` keeps its four
   genuinely different names.
5. **References are padded to the building's own width.** SSC prints
   `<level>.<3 digits>`, so `1.027` and `3.041` become `01.027` and `03.041`.
   Nothing else in SSC needed padding - every room number was already three
   digits. The rule bites on HQ if HQ prints two-digit numbers.

Every row carries the column it was taken from and a note saying why, and the
notes also flag where the result parts company with the delivered SSC ontology.

## What is still open

- `VAV0063` has no room in any column - D reads `(NOT FOUND ON DRAWING LEVEL 3)`
  and E is `#N/A`. Left blank rather than guessed.
- `03.006A` and `03.006B` are not in the delivered SSC ontology, which has one
  `03.006 MEETING ROOM`. The drawings and the screen also disagree on which of
  the two is A: D calls VAV0062's room `03.006B`, the screen calls it `03.006A`.
  Both rows are green, so the screen was followed; the split needs confirming.
  Neither room has a name beyond `ROOM` on the drawings or the screen, so the
  subjects read `entity:SSC_03-006A_Room`.
- Abbreviations are kept as the source wrote them - `Main-Sec-Control-Room`,
  `Assoc-Directors-Office`, `Vent-Plant`. `SEC.` is ambiguous (security or
  secondary) and these become labels users read, so they want expanding once
  the client says what they stand for.
- Labels are written in the QF SSC house style (`1.024 CORRIDOR`), which is what
  the delivered SSC sheet uses. Dar Cairo instead labels a room with its own
  identifier tail (`Corridor-02-B112`).

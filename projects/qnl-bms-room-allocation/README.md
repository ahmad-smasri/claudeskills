# Reading QNL equipment-to-room allocation off the BMS screens

Same job as `../bms-room-allocation` did for HQ and SSC, on the 37 QNL
AVEVA/Wonderware screens: follow the dotted `Display Serving Areas` leader from
every unit widget to the room it serves, and write that room into column J of
the `Controllable Asset Registry`.

The QNL screens are the same product but they are drawn differently, and two
differences break the HQ walker outright:

**Leaders end in a dot.** Every leader finishes in a solid disc about four
pixels across, sitting inside the room. The disc is drawn ~50 grey levels below
the room fill where the leader itself is only ~25 below, so `qnl_dots.py`
separates the two on darkness, drops the one-pixel leaders and two-pixel walls
with a size test, and throws out bold room text by its company - letters come
in runs, a disc stands alone. A leader bend also reads as a small solid blob,
so a blob is only a disc if exactly one of the four headings still carries
stroke away from it.

**Leaders cross the building's outer wall.** The wall is a solid band six to
ten pixels across; inside it the local background is the wall itself, so no
pixel reads as stroke and the walker runs out of dash tolerance and stops -
which is how a unit ends up placed in whatever the wall happens to touch. The
walker steps over a gap only when the gap is *inked*: something is drawn there,
just not stroke. A gap of bare screen is the end of the leader, and stepping
over that is how a unit ends up on the leader of the widget next door.

Two more corrections worth naming, both learned from getting them wrong on the
first basement screen:

- **The corner is not where the run stops.** A horizontal run carries a few
  pixels past its own corner onto whatever wall stub sits beyond. So the corner
  is chosen as the *last* point along the run with a long dashed stroke leaving
  it sideways: walls and duct outlines are solid and refused, and a leader
  merely crossing ours is passed over because a later branch exists.
- **A slider bar's own outline is stroke.** A walker that reaches one climbs on
  to it and finishes inside somebody else's widget - six of thirty-one did
  exactly that. The bars are taken out of the mask before walking.

`trace.is_line` reads the background off the column above and below a pixel,
which is flat under a horizontal stroke and *is the stroke* under a vertical
one, so vertical leaders vanished. `qnl_trace.mask` measures both axes.

## Files

| File | What it does |
|---|---|
| `qnl_dots.py` | finds the discs that terminate the leaders |
| `qnl_trace.py` | the walker: masks, the gap rule, the corner rule |
| `annotate_qnl.py` | traces a screen and writes a numbered copy to read by eye |
| `run_all.sh` | annotates every screen not already done |
| `trace.py`, `crop.py` | symlinks to the HQ/SSC originals - widget finding, zooming |

```
python3 annotate_qnl.py QNL/BF.jpg out.png out.json
```

## Accuracy

The tracer is an aid, not the authority - the same rule as on HQ and SSC, and
for the same reasons. On the first basement screen it resolves 24 of 31 units
to a disc, 22 of them uniquely; two widgets landing on the same disc means at
least one of them is wrong. Every row still needs the endpoint confirming by
eye on the annotated image, and the two rules from the HQ README hold here
too: resolve the room polygon before looking for its label, and zoom before
deciding.

## Reading a screen

Three steps, and the order matters:

1. `labels_qnl.py` writes one strip of the tag printed above every widget,
   numbered exactly as `annotate_qnl.py` numbers them (both sort by `left, y`).
   Thirty tags read in one look instead of thirty zooms.
2. `annotate_qnl.py` writes the traced screen. Red marker = the walk finished
   on a dot; orange = it did not, and the row is not to be written from it;
   hollow blue = a dot nothing claimed, so a leader that was missed.
3. Read the room by eye, zooming. **Resolve the room polygon first, then find
   the label that points into it** - the QNL screens print several room names
   inside one open space and lead each to its own room with a dashed pointer of
   its own, so the nearest text is routinely the wrong answer.

Then `write_j.py` puts the readings into columns J and K of the register,
`report_qnl.py` prints column D against column J, and `highlight_rows.py`
fills the rows that need a human eye.

Two things about the register itself, both learned the hard way. The QNL block
is a **collapsed outline group** - all 551 rows carry `hidden="1"` - so
anything written into it reads as an empty sheet until the group is expanded;
`write_j.py` expands it. And the rows to check are filled `FF00B050`, the green
already used on the HQ and SSC rows, **across the whole row A:K** rather than
one cell, because a later pass reads the row colour.

## What the screens can and cannot settle

Some of these plans are open. The whole top half of `BF` is one space carrying
`Break Out Area` at the west end and `Tech.Services & Collections Office` at
the east with no wall between them - checked at 3x with the contrast raised.
Fourteen units land in it. The register splits them between B.001A and B.001;
the screen does not contradict that, it simply cannot confirm it, so those
rows are written as the open space and reported `OPEN` rather than `SAME` or
`DIFF`. Reading a boundary that is not drawn would be inventing one.

## Coverage

203 of the 551 QNL rows carry a column J reading. The rest are blank on
purpose, and `alloc.BLANK` says why for each one - a guess in column J reads
exactly like a reading, so nothing is written that was not confirmed by eye.

| Screen | Placed | | Screen | Placed |
|---|---|---|---|---|
| BF | 29 | | FF | 20 |
| BF-1 | 10 | | FF-2 | 15 |
| BF-2 | 16 | | FF-3 | 5 |
| BF-3 | 10 | | SF-1 | 26 |
| BF-4 | 6 | | SF-3 | 21 |
| BF-5 | 12 | | SF-6 | 12 |
| BF-6 | 4 | | | |
| BF-7 | 4 | | | |
| BF-8 | 3 | | | |
| BF-10 | 10 | | | |

Four screens carry no slider units at all (BF-9, BF-11, BF-12, and the empty
FF-1, FF-6, FF-8, FF-9, RF-4, SF-2, SF-7, SF-8) and three more - FF-4, FF-5 and
Terrace Floor-1 - print furniture and function labels (Book Shelf, Media
Station, Special Events, Enter) and no room names, so nothing on them can be
matched against column D either way. Column D calls most of those units bridge
ceiling voids, which the QNL screens do not draw.

## What the readings say

`report_qnl.py` gives each row one of five verdicts:

| Verdict | Count | Meaning |
|---|---|---|
| SAME | 88 | the screen and column D name the same room |
| OPEN | 43 | the room is one open space carrying two or more labels; the screen cannot split them, and does not contradict column D |
| CHECK | 52 | read, but with a caveat - usually the dot lands in a space the screen leaves unlabelled |
| DIFF | 19 | the screen puts the unit somewhere column D does not |

The 19 DIFF rows and the 52 CHECK rows - 71 in all - are filled green across
A:K. SAME and OPEN rows are left alone: on those the screen either agrees with
column D or cannot contradict it.

**The largest single finding is not in that table.** Twenty-seven units tagged
`2F` - eleven `VAV-2F-S12` on SF-1 and sixteen `VAV-2F-S14` on SF-3 - carry a
*first floor* room in column D: OPEN READING AREA L1.001, BRAILLE READER
L1.002, STUDENT CARRELS L1.007, PUBLIC SERVICES L1.080, REF LIBRARIAN L1.086
to L1.097. Those rooms are printed on the First Floor Zone 1 screen, not on
the second-floor screens these units appear on. The screens cannot say what the
right rooms are - SF-1's west half carries no label at all and SF-3's units all
land in one open cyan zone - so the rows are written as the space they land in
and flagged. This wants a decision from the client rather than a reading.

The nineteen outright differences are in `QNL_BMS_screen_findings.csv`. Two
patterns run through them: a dot one wall away from the room column D names
(FCU-B-008, S11-037, S11-043, S11-046, S12-029, S13-004, S14-003), and a room
whose column D name disagrees with the column E entity while the screen sides
with the entity (S11-026 Finance Coordinator, S11-038 Procurement SPC).

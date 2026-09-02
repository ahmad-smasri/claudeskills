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

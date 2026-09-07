# Reading equipment-to-room allocation off the RDC BMS screens

The RDC AVEVA screens draw a dotted leader from every unit widget to a small
filled grey dot inside the room it serves. The leader turns square corners,
often several. That leader is the equipment-to-room link, and these scripts
follow it.

```
./run_all.sh                       # trace all 47 screens -> out/
python3 tags.py <screen> t.png 4   # the tag above each unit, in a numbered grid
python3 build.py                   # write the RDC-only workbook
```

## How the screens differ from QNL, SSC and HQ

**The tag is printed above the widget.** On QNL the tag had to be recovered from
a strip and matched back to the register by position; here it can simply be
read, which is why the readings are keyed by tag rather than by widget number.

**The leader is dashed at two weights**, and telling either from a wall is the
whole problem. The thin one runs 154 dark against 188 light - and 154 is exactly
the grey the walls are drawn in, so no brightness threshold separates them. The
first mask used a band between the two weights and found eight leaders out of
forty-three: every thin leader had been classified as wall and erased.

What separates them is direction. A leader is dashed *along its own length*, so
a short window laid along it spans both phases and sees a range of about fifty
grey levels; a wall is solid along its own length and the same window sees
nothing. `rdc_trace.masks` is that test, plus a second one - a leader is
one-dimensional and text is not, so a stroke that fills its window in both axes
is a letter and is dropped. Without that, a walk leaving a widget climbs into
the widget's own printed tag and lands on the bowl of a letter.

**Every screen carries a section-cut line** - dashed, full height, just inside
the outer wall - and most leaders cross it. `_resume` carries a walk straight
through a crossing before it will consider a turn; without it five of the twelve
widgets down the right-hand side of the first screen finished on the cut line.

## The files

| File | What it does |
|---|---|
| `rdc_trace.py` | the stroke mask and the walker: straight runs, corners, wall crossings |
| `rdc_dots.py` | the grey dot that ends a leader - candidates only, the walk confirms them |
| `rdc_widgets.py` | sliders and equipment tiles, plus the tag printed above each |
| `annotate.py` | traces one screen, writes the annotated image, the endpoint JSON and a tag strip |
| `tags.py` | the tags in a numbered grid, so a marker number can be turned into a tag |
| `crop.py` | crop and upscale, for checking a leader by eye |
| `readings.csv` | screen, tag, room, confidence, note - **the readings** |
| `blanks.csv` | screen, tag, reason - the units whose room could not be read |
| `build.py` | joins the readings to the register and writes the workbook |

## Two detectors, because neither finds every widget

A slider is a black bar with a bordered white box to its right, and a red cross
badge when the unit is in alarm. Anchoring on the cross finds every unit in
alarm and no other, so the screens whose units are all healthy came back empty.
Anchoring on the box loses units whose box is partly covered by its own badge.
`rdc_widgets.find` takes the union and deduplicates by position: on the ground
floor screens that is a third more widgets than the structural pass alone.

## Reading, not inferring

The tracer says where to look. The room is named by reading the annotated image,
and where the screen does not settle it - the dot on a wall between two rooms,
or in open floor that carries a name but has no wall - the row goes in
`blanks.csv` with the reason instead. A guessed room reads exactly like a read
one once it is in the sheet, and nobody can tell them apart afterwards.

`confidence` is `ok` where the dot sits clearly inside one named room and
`check` where it is on a boundary or in unbounded floor. `check` rows are filled
green with the rest.

## The join

The screens and the register do not spell a tag the same way, and `build.py`
handles four differences, each of which is documented where it is applied:
the register hyphenates some families (`FEV-5272` against `NB-FEV5272`); it
writes `AHU8601` where the screen writes `AHU-8601`; AHUs carry no level
segment; and the screens label constant-volume terminals CAV where the register
labels them AT. That last one is an inference - one CAV row against 510 AT rows
- so every row joined across it says so in column M.

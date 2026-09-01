# Reading equipment-to-room allocation off the BMS screens

The AVEVA/Wonderware floor-plan screens draw a dotted "serving area" leader from
every unit widget to the room it serves - the `Display Serving Areas` box at the
top right is what turns them on. That leader is the equipment-to-room link, and
these scripts follow it.

- `trace.py` - finds the slider widgets and follows the dotted leaders.
  The stroke is a 3-on/1-off dash drawn about 25 grey levels below whatever is
  behind it, so a fixed threshold fails inside the colour-filled rooms;
  background is estimated per pixel from the column above and below instead.
  Solid room walls are rejected by a duty-cycle test, so only dashed strokes
  are followed.
- `annotate.py` - traces every leader on a screen and writes a copy with a
  numbered marker at each endpoint, plus a JSON of the coordinates. Read the
  annotated image to say which room each marker landed in; the tracer only
  says where to look, it does not name the room.
- `crop.py` - crop and upscale a region, for checking a leader by eye.

```
python3 annotate.py SSC/FF-part1.jpg out.png out.json
```

## Accuracy

The tracer is an aid, not the authority. Two failure modes to check for on
every screen before trusting a row:

- endpoint equals the widget edge - the leader was never picked up (usually a
  leader that leaves vertically, or a unit drawn in alarm red);
- two widgets sharing one endpoint - the walker jumped onto a neighbouring
  leader where they run close together.

Both are visible in the JSON, and both need the endpoint confirming by eye on
the annotated image.

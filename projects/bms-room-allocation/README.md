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

## Reading a leader

Two rules, both learned from getting them wrong:

**Resolve the zone, then find its label.** On the HQ screens a room's name is
printed outside the room and joined to it by its own dashed pointer. So the
question is never "what text is nearest the endpoint" - it is "which room
polygon does the endpoint fall inside", and only then "which label points into
that polygon". VAV0026's leader ends inside G.103; the words `BMS Room` sit
well to the right of it. Reading the nearest text gives the wrong room.

**Zoom before deciding.** At full-screen scale a marker sitting on a wall and a
marker sitting just inside a room look identical. VAV0028's endpoint is 5 px
from the G.003/G.002 wall and the answer changes depending on which side it is.

## Accuracy

The tracer is an aid, not the authority. Two failure modes to check for on
every screen before trusting a row:

- endpoint equals the widget edge - the leader was never picked up (usually a
  leader that leaves vertically, or a unit drawn in alarm red);
- two widgets sharing one endpoint - the walker jumped onto a neighbouring
  leader where they run close together;
- `trace.wall_suspect()` true - the walker stepped off the end of the leader
  onto a wall it touched and followed the wall, sometimes right across the
  plan. Leaders are dashed and walls are not, so an endpoint reached along an
  unbroken run is not a real endpoint. This is what put VAV0026 in the lobby
  and sent FCU0016 the width of the screen away from its own room.

Both are visible in the JSON, and both need the endpoint confirming by eye on
the annotated image.

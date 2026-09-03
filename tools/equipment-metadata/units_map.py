"""Source unit -> Dar Cairo (QUDT) unit, with the factor to apply to the value.

Every target below was chosen from what Dar Cairo actually writes, read off
DarCairo_V93.csv rather than assumed, and re-checked against V98 - the unit
column is identical between the two releases, counts included:

  brick:ratedPowerInput          unit:KiloW      (108 rows)
  brick:coolingCapacity          unit:KiloW      (76)
  para:HighPowerFan et al.       unit:KiloW      (52 each)
  brick:ratedVoltageInput        unit:V          (106)
  brick:electricalPhaseCount     unit:UNITLESS   (106)
  para:ratedSupplyAirFlowrate    unit:L-PER-SEC  (81)
  para:ratedExhaustAirFlowrate   unit:L-PER-SEC  (18)
  para:ratedOutsideAirFlowrate   unit:L-PER-SEC  (18)
  para:ratedChilledWaterFlowrate unit:L-PER-SEC  (83)
  para:ratedWaterFlowrate        unit:L-PER-SEC  (34)
  para:ratedHead                 unit:M          (41)
  rec:area                       unit:M2         (73)
  rec:capacity                   unit:UNITLESS   (64)

So: air flow and water flow both land on L-PER-SEC, power on KiloW, length on M.
unit:PERCENT_RH (27 rows) is distinct from unit:PERCENT (520) and is used for
relative humidity.

`in_dar_cairo=False` marks a QUDT unit that Dar Cairo has never used. Those are
still QUDT terms, not minted ones - Dar Cairo simply carries no mass, mass-flow
or velocity quantity. They are listed on the Units sheet so the PARA team can
confirm them.
"""

# source unit -> (qudt unit, multiply value by, in Dar Cairo, conversion note)
UNIT_MAP = {
    # --- power -------------------------------------------------------------
    "kW":      ("unit:KiloW",   1.0,      True,  ""),
    "W":       ("unit:KiloW",   0.001,    True,  "W / 1000"),
    # --- electrical --------------------------------------------------------
    "A":       ("unit:A",       1.0,      True,  ""),
    "V":       ("unit:V",       1.0,      True,  ""),
    "V DC":    ("unit:V",       1.0,      True,  "DC noted in the property name"),
    "Hz":      ("unit:HZ",      1.0,      True,  ""),
    # --- temperature -------------------------------------------------------
    "degC":    ("unit:DEG_C",   1.0,      True,  ""),
    # --- flow --------------------------------------------------------------
    "m3/s":    ("unit:L-PER-SEC", 1000.0, True,  "m3/s x 1000"),
    "m3/h":    ("unit:L-PER-SEC", 1/3.6,  True,  "m3/h / 3.6"),
    "l/h":     ("unit:L-PER-SEC", 1/3600, True,  "l/h / 3600"),
    "l/s":     ("unit:L-PER-SEC", 1.0,    True,  ""),
    "kg/s":    ("unit:L-PER-SEC", 1.0,    True,
                "water mass flow taken as volume flow at density 1 kg/l; "
                "chilled water at 7-15 degC is ~0.9997 kg/l, a 0.03% difference"),
    # --- pressure ----------------------------------------------------------
    "Pa":      ("unit:PA",      1.0,      True,  ""),
    "kPa":     ("unit:PA",      1000.0,   True,  "kPa x 1000"),
    "mbar":    ("unit:PA",      100.0,    True,  "mbar x 100"),
    "bar":     ("unit:BAR",     1.0,      True,  ""),
    "psig":    ("unit:PA",      6894.757, True,
                "psi x 6894.757; the submittal states it as gauge pressure"),
    # --- length and area ---------------------------------------------------
    "mm":      ("unit:M",       0.001,    True,  "mm / 1000"),
    "m":       ("unit:M",       1.0,      True,  ""),
    "in":      ("unit:M",       0.0254,   True,  "in x 0.0254"),
    "m2":      ("unit:M2",      1.0,      True,  ""),
    "litre":   ("unit:L",       1.0,      False, ""),
    # --- rotation, time, sound --------------------------------------------
    "rpm":     ("unit:RPM",     1.0,      True,  ""),
    "hours":   ("unit:HR",      1.0,      True,  ""),
    "dB":      ("unit:DeciB",   1.0,      True,  ""),
    "dB(A)":   ("unit:DeciB",   1.0,      True,  "A-weighting kept in the property name"),
    # --- dimensionless -----------------------------------------------------
    "n":       ("unit:UNITLESS", 1.0,     True,  ""),
    "set(s)":  ("unit:UNITLESS", 1.0,     True,  ""),
    # --- quantities Dar Cairo does not carry -------------------------------
    "kg":      ("unit:KiloGM",  1.0,      False, ""),
    "lb":      ("unit:KiloGM",  0.45359237, False, "lb x 0.45359237"),
    "kg/h":    ("unit:KiloGM-PER-HR", 1.0, False, ""),
    "g/h":     ("unit:KiloGM-PER-HR", 0.001, False, "g/h / 1000"),
    "m/s":     ("unit:M-PER-SEC", 1.0,    False, ""),
    "kg/m3":   ("unit:KiloGM-PER-M3", 1.0, False, ""),
    "kJ/(kg*K)": ("unit:KiloJ-PER-KiloGM-K", 1.0, False, ""),
    "W/(m*K)": ("unit:W-PER-M-K", 1.0,     False, ""),
    "W/m2 K":  ("unit:W-PER-M2-K", 1.0,    False, ""),
    "cP":      ("unit:CentiP",  1.0,       False, ""),
    "K":       ("unit:K",       1.0,       False, "temperature difference, not a temperature"),
    # --- not quantities ----------------------------------------------------
    "BSP":     ("",             None,     True,  "thread designation, not a quantity"),
    "V-ph-Hz": ("",             None,     True,  "composite nameplate string, not a quantity"),
    "":        ("",             None,     True,  ""),
}

# percent splits by what is being measured
PERCENT_RH = ("unit:PERCENT_RH", 1.0, True, "")
PERCENT    = ("unit:PERCENT",    1.0, True, "")

# properties that are dimensionless quantities even though the sheet prints no unit.
# Matched on whole words, not substrings - "Schedule scope" contains "cop".
DIMENSIONLESS_WORDS = {"shr", "eer", "cop"}
DIMENSIONLESS_PHRASES = {"fan speed setting", "specific gravity"}

def resolve(unit, prop):
    """Return (qudt_unit, factor, in_dar_cairo, note) for one row."""
    p = (prop or "").lower()
    if unit == "%":
        return PERCENT_RH if ("rh" in p.split() or "humidity" in p) else PERCENT
    if unit == "":
        import re as _re
        words = set(_re.findall(r"[a-z]+", p))
        if (words & DIMENSIONLESS_WORDS) or p in DIMENSIONLESS_PHRASES:
            return ("unit:UNITLESS", 1.0, True, "dimensionless ratio")
    return UNIT_MAP.get(unit, ("", None, True, "unmapped source unit"))


import re

_NUM = re.compile(r"^-?\d+(?:\.\d+)?$")

def _sig(x, sig=6):
    """Round to `sig` significant figures and drop a trailing .0."""
    if x == 0:
        return 0
    from math import log10, floor
    d = sig - int(floor(log10(abs(x)))) - 1
    v = round(x, max(d, 0)) if d >= 0 else round(x, d)
    return int(v) if float(v).is_integer() else v

def convert(value, factor):
    """Apply `factor` to every number inside `value`, preserving its shape.

    Handles the shapes these submittals actually print:
      12.5              a plain number
      1 x 0.35          quantity x value  (Euroclima / Emerson fan and compressor rows)
      595X595X48        W x H x D filter element dimensions
      92 / 90 / 93 ...  octave-band series
    Anything else is returned unchanged with converted=False.
    """
    if factor is None:
        return value, False
    if isinstance(value, (int, float)):
        return _sig(value * factor), True
    s = str(value).strip()
    if _NUM.match(s):
        return _sig(float(s) * factor), True
    if factor == 1.0:
        return value, True
    # octave-band series
    if " / " in s:
        parts = [p.strip() for p in s.split(" / ")]
        if all(_NUM.match(p) for p in parts):
            return " / ".join(str(_sig(float(p) * factor)) for p in parts), True
    # quantity x value  ("1 x 0.35", "1x4.5", "2 x 8.175")
    m = re.match(r"^(\d+)\s*[xX]\s*(-?\d+(?:\.\d+)?)$", s)
    if m:
        return "%s x %s" % (m.group(1), _sig(float(m.group(2)) * factor)), True
    # dimension string ("595X595X48")
    parts = re.split(r"[xX]", s)
    if len(parts) >= 2 and all(_NUM.match(p.strip()) for p in parts):
        return " x ".join(str(_sig(float(p.strip()) * factor)) for p in parts), True
    return value, False

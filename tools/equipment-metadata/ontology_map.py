"""Which transcribed properties actually belong in the ontology.

The three delivered reference models agree on a short vocabulary for equipment
metadata. Counting predicates across them:

  Dar Cairo   brick:ratedPowerInput 108, brick:ratedVoltageInput 106,
              brick:electricalPhaseCount 106, para:ratedChilledWaterFlowrate 83,
              para:ratedSupplyAirFlowrate 81, brick:coolingCapacity 76,
              para:ratedHead 41, para:ratedWaterFlowrate 34,
              para:ratedExhaustAirFlowrate 18, para:ratedOutsideAirFlowrate 18,
              para:ratedSpeed 7, para:Rated_Tank_Level 3, para:refrigerant 2
  QF SSC      para:ratedSupplyAirFlowrate 113, para:ratedReheatCapacity 108,
              brick:coolingCapacity 16, brick:ratedPowerInput 7,
              para:ratedFrequency/Power/Voltage 6 each
  QF HQ v0.4  para:ratedSupplyAirFlowrate 628, para:ratedReheatCapacity 602,
              brick:coolingCapacity 158, brick:ratedPowerInput 113,
              brick:ratedVoltageInput 71, brick:electricalPhaseCount 71

and as subject literals: rec:modelNumber, rec:manufacturedBy,
rec:installationDate, para:vavBoxType, para:inletSize, para:outletSize,
para:plenumBoxSize.

That is roughly twenty predicates. Everything else this workbook carries -
dimensions, weights, materials, seal specifications, sound power levels, filter
part numbers, psychrometrics, warranty text - has no precedent in any of them.

Scope values
  core      matches a predicate the reference models actually use, unambiguously
  candidate plausible but needs a decision before it is written
  reference no predicate in any reference model; keep for engineering reference
"""

# (component contains, property equals, predicate, scope, note)
# First match wins; None means "any".
RULES = [
 # ---- identification ---------------------------------------------------
 # A component's own maker is not the equipment's - matched before the general rule.
 ("Mechanical seal", "Manufacturer", "", "reference",
  "the seal maker, not the pump's manufacturer"),
 ("Drive motor", "Motor supplier", "", "reference",
  "the motor maker; rec:manufacturedBy on the motor sub-entity would need that entity first"),
 (None, "Make",               "rec:manufacturedBy", "core", ""),
 (None, "Manufacturer",       "rec:manufacturedBy", "core", ""),
 (None, "Model",              "rec:modelNumber",    "core", ""),
 (None, "Model number",       "rec:modelNumber",    "core", ""),
 (None, "Fan model",          "rec:modelNumber",    "core",
  "on the fan sub-entity, not the parent unit"),
 (None, "Indoor unit model",  "rec:modelNumber",    "core", ""),
 (None, "Outdoor unit model", "rec:modelNumber",    "candidate",
  "belongs on the condensing unit entity, which this workbook does not yet carry"),
 (None, "Date installed",     "rec:installationDate", "core", ""),
 (None, "Refrigerant",        "para:refrigerant",   "core", ""),

 # ---- air flow ---------------------------------------------------------
 ("Supply fan",  "Air flow",  "para:ratedSupplyAirFlowrate", "core", ""),
 ("Return fan",  "Air flow",  "para:ratedExhaustAirFlowrate", "candidate",
  "Dar Cairo has no return-air predicate; exhaust is the nearest"),
 ("Air", "Flow rate",         "para:ratedSupplyAirFlowrate", "core", ""),
 ("Air", "Air flow",          "para:ratedExhaustAirFlowrate", "core",
  "these are exhaust fans"),
 ("Air", "Air flow (per box)","para:ratedSupplyAirFlowrate", "core", ""),
 ("Design condition", "Unit airflow", "para:ratedSupplyAirFlowrate", "core", ""),
 ("Pump design", "Duty flow", "para:ratedChilledWaterFlowrate", "core", ""),

 # ---- water flow and head ---------------------------------------------
 ("Cooling coil", "Water flow", "para:ratedChilledWaterFlowrate", "core", ""),
 ("Fluid", "Flow rate",       "para:ratedChilledWaterFlowrate", "core", ""),
 ("Performance", "CHW flow rate", "para:ratedChilledWaterFlowrate", "core", ""),
 ("CHW flow rate", "Cold side", "para:ratedChilledWaterFlowrate", "core", ""),
 ("CHW flow rate", "Hot side", "para:ratedWaterFlowrate", "candidate",
  "hot side of the exchanger; ratedWaterFlowrate is the generic predicate"),
 ("CW coil", "Unit fluid flow", "para:ratedChilledWaterFlowrate", "core", ""),
 ("Design condition", "Unit fluid flow", "para:ratedChilledWaterFlowrate", "core", ""),
 ("Pump design", "Duty head", "para:ratedHead", "core",
  "Dar Cairo writes ratedHead in metres; this value is kPa"),

 # ---- capacity ---------------------------------------------------------
 ("Cooling coil", "Total capacity", "brick:coolingCapacity", "core", ""),
 ("Electric coil", "Total capacity", "para:ratedReheatCapacity", "core", ""),
 ("Capacity", "Total capacity (cooling)", "brick:coolingCapacity", "core", ""),
 ("Unit performance", "Total cooling capacity", "brick:coolingCapacity", "core", ""),
 ("Option - electrical re-heating", "Max re-heating capacity",
  "para:ratedReheatCapacity", "core", ""),
 ("Heating", "Heating capacity", "para:ratedReheatCapacity", "core", ""),
 ("Construction", "Duty",     "brick:coolingCapacity", "candidate",
  "heat exchanger duty; the reference models only use coolingCapacity on coils and units"),
 ("Thermal specification", "Heat exchanged", "brick:coolingCapacity", "candidate", ""),

 # ---- electrical -------------------------------------------------------
 ("motor", "Rating",          "brick:ratedPowerInput", "core", ""),
 ("Drive motor", "Motor size","brick:ratedPowerInput", "core", ""),
 ("Other data", "Max. absorbed power", "brick:ratedPowerInput", "core", ""),
 ("Unit performance", "Unit power input", "brick:ratedPowerInput", "core", ""),
 ("Drive motor", "Motor speed", "para:ratedSpeed", "core", ""),
 (None, "Speed",              "para:ratedSpeed", "core", ""),
 ("motor", "Full load speed", "para:ratedSpeed", "core", ""),

 # ---- tank -------------------------------------------------------------
 ("Expansion tank", "Capacity", "para:Rated_Tank_Level", "candidate",
  "Dar Cairo uses Rated_Tank_Level 3 times; confirm it means tank volume"),
]

_QUANTITY = {"rec:manufacturedBy", "rec:modelNumber", "rec:installationDate"}

def classify(component, prop):
    """Return (predicate, scope, note) for one transcribed property."""
    c = (component or "").lower()
    for comp, name, pred, scope, note in RULES:
        if name != prop:
            continue
        if comp is not None and comp.lower() not in c:
            continue
        return pred, scope, note
    return "", "reference", ""

def is_literal(pred):
    """True when the predicate is written as a subject literal, not a blank node."""
    return pred in _QUANTITY

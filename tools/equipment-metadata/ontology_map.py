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

Brick 1.4 is checked FIRST, per the class ladder - it is step 2, the reference
models are step 3. Its complete entity-property list is short:

  brick:area, grossArea, netArea, panelArea, volume, azimuth, tilt, coordinates,
  latitude, longitude, yearBuilt, buildingPrimaryFunction,
  buildingThermalTransmittance, thermalTransmittance, ambientTemperatureOfMeasurement,
  conversionEfficiency, measuredModuleConversionEfficiency, ratedModuleConversionEfficiency,
  coolingCapacity, currentFlowType, electricalComplexPower, electricalFlow,
  electricalPhaseCount, electricalPhases, measuredPowerInput, measuredPowerOutput,
  operationalStage, operationalStageCount, ratedCurrentInput, ratedCurrentOutput,
  ratedMaximum/MinimumCurrentInput/Output, ratedMaximum/MinimumVoltageInput/Output,
  ratedPowerInput, ratedPowerOutput, ratedVoltageInput, ratedVoltageOutput,
  resolution, temperatureCoefficientofPmax, lastKnownValue, aggregate, value, hasUnit

Notably Brick has NO water or air flow-rate entity property and NO heat-exchanger
duty property, which is why Dar Cairo minted para:ratedWaterFlowrate,
para:ratedChilledWaterFlowrate and the air-flowrate family in the first place.

Scope values
  core      maps unambiguously to a Brick 1.4 entity property or a predicate the
            reference models use
  candidate plausible but needs a decision before it is written
  reference no predicate in Brick or any reference model; keep as engineering reference
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
 (None, "Outdoor unit model", "rec:modelNumber",    "core",
  "goes on a brick:Condensing_Unit entity - Brick 1.4 carries that class, so no para: is needed"),
 (None, "Date installed",     "rec:installationDate", "core", ""),
 (None, "Refrigerant",        "para:refrigerant",   "core", ""),

 # ---- air flow ---------------------------------------------------------
 ("Supply fan",  "Air flow",  "para:ratedSupplyAirFlowrate", "core", ""),
 ("Return fan",  "Air flow",  "para:ratedExhaustAirFlowrate", "core",
  "Brick has no air-flowrate entity property; Dar Cairo's exhaust predicate confirmed by the user"),
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
 ("CHW flow rate", "Hot side", "para:ratedWaterFlowrate", "core",
  "Brick 1.4 has no water-flowrate entity property at all; Dar Cairo's generic para: term is the "
  "next rung of the ladder and already exists"),
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
 ("Construction", "Duty",     "brick:coolingCapacity", "core",
  "Brick 1.4 has no heat-exchanger duty property; coolingCapacity is the Brick term and these "
  "exchangers deliver cooling to the secondary loop"),
 ("Thermal specification", "Heat exchanged", "brick:coolingCapacity", "core",
  "same Brick term as the duty above"),

 # ---- Brick 1.4 terms this workbook can fill ---------------------------
 (None, "Full load current",  "brick:ratedCurrentInput", "core",
  "Brick 1.4 entity property; no reference model uses it yet"),
 ("Drive motor", "Motor speed", "para:ratedSpeed", "core", ""),
 ("Air", "Number of speeds",  "brick:operationalStageCount", "core",
  "Brick 1.4 entity property - a 3-speed fan has 3 operational stages"),

 # ---- electrical -------------------------------------------------------
 ("motor", "Rating",          "brick:ratedPowerInput", "core", ""),
 ("Drive motor", "Motor size","brick:ratedPowerInput", "core", ""),
 ("Other data", "Max. absorbed power", "brick:ratedPowerInput", "core", ""),
 ("Unit performance", "Unit power input", "brick:ratedPowerInput", "core", ""),
 ("Drive motor", "Motor speed", "para:ratedSpeed", "core", ""),
 (None, "Speed",              "para:ratedSpeed", "core", ""),
 ("motor", "Full load speed", "para:ratedSpeed", "core", ""),

 # ---- tank -------------------------------------------------------------
 ("Expansion tank", "Capacity", "para:Rated_Tank_Level", "core",
  "chosen by the user. Note brick:volume exists in Brick 1.4 and by the ladder would outrank a "
  "para: term for a tank volume - reversible in one line if the team prefers it"),
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


# Where each predicate comes from, in class-ladder order:
# Brick 1.4 first, then a para: term a reference model already coined.
PREDICATE_SOURCE = {
 "brick:coolingCapacity":         "Brick 1.4 - also used by Dar Cairo, SSC, HQ",
 "brick:ratedPowerInput":         "Brick 1.4 - also used by Dar Cairo, SSC, HQ",
 "brick:ratedCurrentInput":       "Brick 1.4 - not yet used by any reference model",
 "brick:operationalStageCount":   "Brick 1.4 - not yet used by any reference model",
 "para:ratedSupplyAirFlowrate":   "para: - Dar Cairo 81, SSC 113, HQ 628 (Brick has no air flowrate)",
 "para:ratedExhaustAirFlowrate":  "para: - Dar Cairo 18 (Brick has no air flowrate)",
 "para:ratedChilledWaterFlowrate":"para: - Dar Cairo 83 (Brick has no water flowrate)",
 "para:ratedWaterFlowrate":       "para: - Dar Cairo 34 (Brick has no water flowrate)",
 "para:ratedReheatCapacity":      "para: - SSC 108, HQ 602 (Brick has no reheat capacity)",
 "para:ratedHead":                "para: - Dar Cairo 41 (Brick has no head)",
 "para:ratedSpeed":               "para: - Dar Cairo 7 (Brick Rotational_Speed is a quantity, not a property)",
 "para:refrigerant":              "para: - Dar Cairo 2",
 "para:Rated_Tank_Level":         "para: - Dar Cairo 3; brick:volume would outrank it by the ladder",
 "rec:modelNumber":               "REC - Dar Cairo 411, SSC 126, HQ 777",
 "rec:manufacturedBy":            "REC - Dar Cairo 449, SSC 7, HQ 42",
 "rec:installationDate":          "REC - Dar Cairo 494",
}

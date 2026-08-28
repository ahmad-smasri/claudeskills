# Plate heat exchangers - SCHEDULE OF HEAT EXCHANGER
# Source: MEP schedule drawing, supplied as an image in chat. The image crops the
# title block, so the drawing number and sheet are not recoverable from it.
SRC_HEX = "MEP schedule drawing (image supplied in chat)"
PAGE_HEX = "SCHEDULE OF HEAT EXCHANGER"

HEX_COLS = ["unit_ref","type","location","dim_lxwxh_mm","operating_weight_kg",
            "chw_flow_cold_l_s","chw_flow_hot_l_s","make","qty"]

HEX_ROWS = [
 ["PHX/B/01","COUNTER CURRENT","PLANT ROOM-4","2735x780x2165",4430,62.8,62.2,"ALFA LAVAL",1],
 ["PHX/B/02","COUNTER CURRENT","PLANT ROOM-4","2735x780x2165",4430,62.8,62.2,"ALFA LAVAL",1],
 ["PHX/B/03","COUNTER CURRENT","PLANT ROOM-4","2735x780x2165",4430,62.8,62.2,"ALFA LAVAL",1],
 ["PHX/B/04","COUNTER CURRENT","PLANT ROOM-4","2735x780x2165",4430,62.8,62.2,"ALFA LAVAL",1],
]

HEX_NOTES = [
 ("Source reference", "The supplied image crops the drawing title block, so the drawing number, "
  "sheet number and revision are not recorded. Ask for the sheet reference before handover."),
 ("Schedule scope", "The schedule gives dimensions, operating weight and CHW flow rate only. It "
  "states no duty, no plate count, no design pressure and no connection sizes - those were not "
  "inferred."),
]


# ---------------------------------------------------------------------------
# Alfa Laval construction data, the M10-MFM thermal specification, and the
# SYSTEM DETAILS equipment schedule. These add a FIFTH exchanger, PHX/B/05,
# which is not on the drawing schedule above.
SRC_AL   = "Alfa Laval plate heat exchanger data (image supplied in chat)"
PAGE_AL  = "PHE construction comparison - QF Central Library"
SRC_ALTS = "Alfa Laval Plate Heat Exchanger Technical Specification (image supplied in chat)"
PAGE_ALTS = "PHX/B/05-300 KW A, M10-MFM, 5/21/2012"
SRC_SYS  = "SYSTEM DETAILS (image supplied in chat)"
PAGE_SYS = "Table 3.3 - Heat Exchangers Equipment Schedule"

HEX_PROJECT = [
 ("Project", "Project", "QF Central Library", ""),
 ("Project", "Contractor", "Mercury Engineering Qatar", ""),
 ("Project", "Consultant", "ASTAD Project Management", ""),
]

# Construction data per model, from the comparison table.
HEX_MODELS = {
 "T20-BFG": dict(
   item_reference="PHX/B/01-04-2350 KW", duty_kw=2350, plates=423,
   plate_material="Stainless Steel 316", plate_thickness_mm=0.6,
   area_m2=380.7, u_dirty_clean="5890 / 6478 (dirty / clean)",
   packed_dims_mm="3000 x 890 x 2500", packed_weight_kg=3810,
   overall_dims_mm="2735 x 780 x 2165", net_weight_empty_kg=3640,
   net_weight_operating_kg=4430),
 "M10-MFM": dict(
   item_reference="PHX/B/05-300 KW", duty_kw=300, plates=19,
   plate_material="Stainless Steel 316", plate_thickness_mm=0.6,
   area_m2=4.18, u_dirty_clean="3408 / 3613 (dirty / clean)",
   packed_dims_mm="1145 x 600 x 930", packed_weight_kg=327,
   overall_dims_mm="720 x 470 x 1084", net_weight_empty_kg=297,
   net_weight_operating_kg=315),
}

HEX_MODEL_FIELDS = [
 ("item_reference", "Item reference", ""),
 ("duty_kw", "Duty", "kW"),
 ("plates", "Number of plates", "n"),
 ("plate_material", "Plate material", ""),
 ("plate_thickness_mm", "Plate thickness", "mm"),
 ("area_m2", "Effective heat transfer area", "m2"),
 ("u_dirty_clean", "Overall heat transfer coefficient", "W/m2 K"),
 ("packed_dims_mm", "Packed dimensions per PHE (L x W x H)", "mm"),
 ("packed_weight_kg", "Packed weight per PHE", "kg"),
 ("overall_dims_mm", "Overall dimensions per PHE (L x W x H)", "mm"),
 ("net_weight_empty_kg", "Net weight, empty", "kg"),
 ("net_weight_operating_kg", "Net weight, operating", "kg"),
]

# Duty / standby designation and model, from the SYSTEM DETAILS schedule.
HEX_DUTY = {
 "PHX/B/01": ("Duty HEX", "T20-BFG"), "PHX/B/02": ("Duty HEX", "T20-BFG"),
 "PHX/B/03": ("Duty HEX", "T20-BFG"), "PHX/B/04": ("Standby HEX", "T20-BFG"),
 "PHX/B/05": ("Main HEX", "M10-MFM"),
}
HEX_SYS_TEMPS = [
 ("Hot side temperature", "15.5 degC in, 6.5 degC out"),
 ("Cold side temperature", "5.5 degC in, 14.4 degC out"),
]

# The fifth exchanger, absent from the drawing schedule.
HEX_EXTRA_UNITS = ["PHX/B/05"]

# M10-MFM thermal specification, per side. (property, unit, hot, cold)
M10_SPEC = [
 ("Fluid", "", "Water", "Water"),
 ("Density", "kg/m3", 993.8, 1000),
 ("Specific heat capacity", "kJ/(kg*K)", 4.18, 4.21),
 ("Thermal conductivity", "W/(m*K)", 0.620, 0.585),
 ("Viscosity inlet", "cP", 0.546, 1.50),
 ("Viscosity outlet", "cP", 1.01, 1.16),
 ("Volume flow rate", "l/s", 2.4, 8.0),
 ("Inlet temperature", "degC", 50.0, 5.5),
 ("Outlet temperature", "degC", 20.0, 14.4),
 ("Pressure drop", "kPa", 4.44, 46.9),
 ("Number of passes", "n", 1, 1),
 ("Sealing material", "", "NBRP CLIP-ON", "NBRP CLIP-ON"),
 ("Connection diameter", "", "DN100", "DN100"),
 ("Nozzle orientation", "", "S1 -> S2", "S4 <- S3"),
 ("Design pressure", "bar", 10.0, 10.0),
 ("Test pressure", "bar", 13.0, 13.0),
 ("Design temperature", "degC", 120.0, 120.0),
]
# Whole-unit values on the same specification.
M10_UNIT = [
 ("Customer", "Mercury Qatar", ""),
 ("Project", "AEDUBMY-1304(c)/J-20111017-Mercury-Ctrl Library BP#7A", ""),
 ("Item", "PHX/B/05-300 KW A", ""),
 ("Specification date", "5/21/2012", ""),
 ("Heat exchanged", 300.0, "kW"),
 ("L.M.T.D.", 23.5, "K"),
 ("Relative directions of fluids", "Countercurrent", ""),
 ("Plate material / thickness", "ALLOY 316 / 0.60 mm", ""),
 ("Pressure vessel code", "PED", ""),
 ("Flange rating", "DIN PN10", ""),
 ("Overall length x width x height", "720 x 470 x 1084", "mm"),
]

HEX_EXTRA_NOTES = [
 ("A fifth exchanger", "The drawing schedule carries PHX/B/01 to PHX/B/04 only. The Alfa Laval "
  "data and the SYSTEM DETAILS schedule both add PHX/B/05, a 300 kW M10-MFM described as the "
  "'Main HEX'. It is included here on that basis."),
 ("Duty split", "SYSTEM DETAILS names PHX/B/01 to 03 as duty, PHX/B/04 as standby and PHX/B/05 as "
  "the main HEX. The drawing schedule states no duty split."),
 ("Temperature conflict on PHX/B/05", "SYSTEM DETAILS gives one hot-side figure across all five "
  "rows - 15.5 degC in, 6.5 degC out. The Alfa Laval specification for the M10-MFM gives 50.0 "
  "degC in, 20.0 degC out on the hot side. The cold side agrees at 5.5 in / 14.4 out. Both are "
  "recorded against their own source; the conflict is unresolved."),
 ("Weights cross-check", "The Alfa Laval net operating weight for the T20-BFG, 4430 kg, and its "
  "overall dimensions, 2735 x 780 x 2165 mm, both match the drawing schedule exactly."),
 ("Flow rate is per unit", "The drawing schedule's 62.8 / 62.2 l/s is per exchanger. The Alfa "
  "Laval sheet gives 2350 kW per T20-BFG."),
]

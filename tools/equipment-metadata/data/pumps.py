# Chilled water pumps - SCHEDULE OF PUMPS
# Source: MEP schedule drawing, supplied as an image in chat (same sheet as the
# heat exchanger and pressurization unit schedules).
SRC_PUMP = "MEP schedule drawing (image supplied in chat)"
PAGE_PUMP = "SCHEDULE OF PUMPS"

PUMP_COLS = ["unit_ref","type","location","model","dim_lxwxh_mm","weight_kg",
             "chw_flow_l_s","make","qty"]

PUMP_ROWS = [
 ["CHWP/B/01","HORIZONTAL SPLIT CASE","PLANT ROOM-4","4600-STARFLO-125-380H-55KW",
  "1727x760x760",843,62.3,"ARMSTRONG",1],
 ["CHWP/B/02","HORIZONTAL SPLIT CASE","PLANT ROOM-4","4600-STARFLO-125-380H-55KW",
  "1727x760x760",843,62.3,"ARMSTRONG",1],
 ["CHWP/B/03","HORIZONTAL SPLIT CASE","PLANT ROOM-4","4600-STARFLO-125-380H-55KW",
  "1727x760x760",843,62.3,"ARMSTRONG",1],
 ["CHWP/B/04","HORIZONTAL SPLIT CASE","PLANT ROOM-4","4600-STARFLO-125-380H-55KW",
  "1727x760x760",843,62.3,"ARMSTRONG",1],
]

PUMP_NOTES = [
 ("Source reference", "The supplied image crops the drawing title block, so the drawing number, "
  "sheet number and revision are not recorded. Ask for the sheet reference before handover."),
 ("Motor rating", "The model designation ends in '55KW', which reads as a 55 kW motor. The schedule "
  "states no motor rating of its own, so no rated-power property was created from it. Confirm "
  "against the pump submittal before writing brick:ratedPowerInput."),
 ("Schedule scope", "The schedule gives no head, no speed, no efficiency and no electrical data - "
  "those were not inferred."),
]


# ---------------------------------------------------------------------------
# Armstrong submittal TENDER301358.1 rev3, page 14/22, and the SYSTEM DETAILS
# equipment schedule. Both cover the same four pumps as the drawing schedule
# above, so this data is attached to CHWP/B/01 .. CHWP/B/04.
SRC_SUB = "Armstrong submittal TENDER301358.1 rev3 (image supplied in chat)"
PAGE_SUB = "Page 14/22 - 4600 Starflo-125-380H-55 kW"
SRC_SYS = "SYSTEM DETAILS (image supplied in chat)"
PAGE_SYS = "Table 3.1 - Chilled Water Pumps Equipment Schedule"

PUMP_TAGS = ["CHWP/B/01", "CHWP/B/02", "CHWP/B/03", "CHWP/B/04"]

# Duty / standby split and the alternate tag shape, from the SYSTEM DETAILS table.
PUMP_DUTY = {"CHWP/B/01": ("Duty Pump", "CHWP-B-01"),
             "CHWP/B/02": ("Duty Pump", "CHWP-B-02"),
             "CHWP/B/03": ("Duty Pump", "CHWP-B-03"),
             "CHWP/B/04": ("Standby Pump", "CHWP-B-04")}

# (component, property, value, unit, note) - identical across all four pumps
PUMP_SUBMITTAL = [
 ("Submittal", "Project number", "301358.1.3", "", ""),
 ("Submittal", "Project name", "Central Library - Qatar", "", ""),
 ("Submittal", "Reference", "TENDER301358.1.3", "", ""),
 ("Submittal", "Project location", "DOHA", "", ""),
 ("Submittal", "Representative", "PETROFAC QATAR W.L.L.", "", ""),
 ("Submittal", "Submitted by", "M Aashik", "", "Dated 8/8/2012"),
 ("Submittal", "Type", "HORZ", "", "Horizontal"),

 ("Pump design", "Tag num", "BP#7A", "", "The project/package reference, not a pump tag"),
 ("Pump design", "Service", "Chilled Water Pump", "", ""),
 ("Pump design", "Quantity", 4, "n", "Submittal covers all four pumps"),
 ("Pump design", "Duty flow", 62.3, "l/s", ""),
 ("Pump design", "Duty head", 460, "kPa", ""),
 ("Pump design", "Pipe orientation", "Parallel", "", ""),
 ("Pump design", "Pump run quantity", 3, "n", "Three of the four run; the fourth is standby"),
 ("Pump design", "Suction pressure", 0, "psig", ""),
 ("Pump design", "Fluid", "Water", "", ""),
 ("Pump design", "Operating temperature", 15.55, "degC", ""),
 ("Pump design", "Viscosity", "31 SSU", "", "Saybolt Universal Seconds - no QUDT unit"),
 ("Pump design", "Specific gravity", 1.0000, "", ""),
 ("Pump design", "Suction", 6, "in", ""),
 ("Pump design", "Discharge", 5, "in", ""),

 ("Drive motor", "Motor supplier", "WEG", "", ""),
 ("Drive motor", "Motor size", 55, "kW", ""),
 ("Drive motor", "Motor frame number", "250M", "", ""),
 ("Drive motor", "Motor enclosure", "TEFC", "", "Totally enclosed fan cooled"),
 ("Drive motor", "Power supply", "400/3/50", "", ""),
 ("Drive motor", "Motor efficiency class", "IE3", "", ""),
 ("Drive motor", "Insulation class", "Class F Insulation", "", ""),
 ("Drive motor", "Inverter motor type", "[none]", "", "Stated as none on the submittal"),
 ("Drive motor", "Motor speed", 1500, "rpm", ""),

 ("Mechanical seal", "Manufacturer", "Armstrong", "", ""),
 ("Mechanical seal", "Seal type", "Inside Unbalanced", "", ""),
 ("Mechanical seal", "Manufacturer code", "21A", "", ""),
 ("Mechanical seal", "Rotating face", "Resin Bonded Carbon", "", ""),
 ("Mechanical seal", "Stationary seat", "Silicon Carbide", "", ""),
 ("Mechanical seal", "Secondary seal", "EPDM", "", ""),
 ("Mechanical seal", "Springs", "Stainless Steel", "", ""),
 ("Mechanical seal", "Rotating hardware", "Stainless Steel", "", ""),
 ("Mechanical seal", "Fluid type", "Non-Potable Fluid", "", ""),
 ("Mechanical seal", "Seal", "A5: Armstrong 21A", "", ""),

 ("Materials of construction", "Construction", "CI/GM", "", "Cast iron / gunmetal"),
 ("Materials of construction", "Rating", "PN-16", "", ""),
 ("Materials of construction", "Impeller", "Gunmetal Bronze (BS1400 LG2C)", "", ""),
 ("Materials of construction", "Shaft sleeve", "SS (BS970 304)", "", ""),
 ("Materials of construction", "Flexible couplings", "Standard", "", ""),
 ("Materials of construction", "Pump shaft", "SS (BS970 416)", "", ""),
 ("Materials of construction", "Flush line", "Braided Stainless Steel", "", ""),
 ("Materials of construction", "Casing gasket", "Velotherm (Non-Asbestos fiber)", "", ""),
 ("Materials of construction", "Bearings", "Anti-Friction Grease Lubricated", "", ""),
 ("Materials of construction", "Pump casing", "Cast Iron", "", ""),
 ("Materials of construction", "Pump suction", "Right-hand when viewed from Drive End", "", ""),
 ("Materials of construction", "Suction/discharge flange",
  "BS EN 1092-2:1997 PN16/PN16 Cast Iron", "", ""),
 ("Materials of construction", "Size", "125-380H", "", ""),
 ("Materials of construction", "Hydrostatic test",
  "Pump casings are hydrostatically tested to 150% of maximum pump working pressure", "", ""),

 ("Dimensional data", "Configuration code", "4600125-380HPN16250MTEFC", "", ""),
 ("Dimensional data", "D",  15,    "in", "Drawing callout; the submittal does not name the feature"),
 ("Dimensional data", "HA", 19,    "in", "Drawing callout"),
 ("Dimensional data", "HB", 64,    "in", "Drawing callout"),
 ("Dimensional data", "HC", 68.06, "in", "Drawing callout"),
 ("Dimensional data", "HD", 16,    "in", "Drawing callout"),
 ("Dimensional data", "HE", 8.5,   "in", "Drawing callout"),
 ("Dimensional data", "HF", 30,    "in", "Drawing callout"),
 ("Dimensional data", "HG", 6,     "in", "Drawing callout"),
 ("Dimensional data", "HL", 13.5,  "in", "Drawing callout"),
 ("Dimensional data", "HM", 30,    "in", "Drawing callout"),
 ("Dimensional data", "HO", 30.03, "in", "Drawing callout"),
 ("Dimensional data", "HP", 2,     "in", "Drawing callout"),
 ("Dimensional data", "S",  15,    "in", "Drawing callout"),
 ("Dimensional data", "SD", 30,    "in", "Drawing callout"),
 ("Dimensional data", "Weight", 1874, "lb", ""),
]

PUMP_SUB_NOTES = [
 ("Submittal dimensions are imperial", "The dimensional block is headed '(in, lb) NOT for "
  "CONSTRUCTION'. Values are inches and pounds and are converted on that basis. The block is "
  "marked not for construction, so do not build to it."),
 ("Weight disagreement", "The submittal gives 1874 lb, which is 850 kg. The drawing schedule "
  "gives 843 kg. A 7 kg difference - probably a different scope of supply (baseplate, coupling "
  "guard) rather than an error, but neither document says."),
 ("Dimension callouts are unlabelled", "D, HA, HB, HC and the rest are letters keyed to the "
  "outline drawing. The submittal does not say which feature each measures, so they are recorded "
  "as callouts rather than named dimensions."),
 ("Duty and standby", "The SYSTEM DETAILS schedule names CHWP-B-01 to 03 as duty pumps and "
  "CHWP-B-04 as the standby. That matches the submittal's 'Pump Run Qty 3' against 'Qty 4'."),
 ("Alternate tag shape", "The SYSTEM DETAILS schedule writes the tags with dashes (CHWP-B-01) "
  "where the drawing schedule writes slashes (CHWP/B/01). The slash form is used as the tag here "
  "because it matches every other reference in this workbook; the dash form is recorded against "
  "each pump as an alternate reference. Confirm which the BMS uses."),
 ("Tag Num on the submittal", "The submittal's 'Tag Num' field reads BP#7A, which is the Education "
  "City building package reference, not a pump tag. It does not identify an individual pump."),
]

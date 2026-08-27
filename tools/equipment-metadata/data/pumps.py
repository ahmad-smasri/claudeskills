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

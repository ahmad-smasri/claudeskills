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

# Standby generators - GENERATOR ASSET LIST
# Source: an asset-register table supplied as an image in chat. The image is cropped:
# the first data row is complete, the second is cut off mid-row and any rows below it
# are not visible at all. Only the complete row is transcribed.
SRC_GEN = "GENERATOR ASSET LIST (image supplied in chat)"
PAGE_GEN = "GENERATOR ASSET LIST"

GEN_COLS = ["asset_tag", "location_info", "main_category", "sub_category", "manufacturer",
            "model_number", "serial_number", "equipment_name", "building_name", "floor",
            "room_no", "date_installed", "quantity", "pm_procedure_description",
            "procedure_document", "warranty", "warranty_expires", "warranty_notes",
            "recommended_spare_parts"]

GEN_ROWS = [
 ["GENERATOR SET", "QNL", "STANDBY GENERATOR", "DIESEL GENERATOR", "CTM",
  "4012-46TAG3A", "11 211 038571-16", "GENERATOR SET", "QATAR NATIONAL LIBRARY",
  "LOWER LEVEL", "B080", "Jun-12", 1, "REFER O&M", "REFER O&M", "YES",
  "12 MONTHS FROM COC", "12 MONTHS FROM DATE OF COMMISSIONING", "REFER O&M"],
]

GEN_NOTES = [
 ("One generator, not a truncated list", "The image cuts off partway through the row below, but "
  "the user has confirmed that row belongs to a different piece of equipment. The asset list is a "
  "multi-equipment register rather than a generator inventory, so the single row transcribed here "
  "is the complete record for this generator."),
 ("Asset tag is not unique", "The ASSET TAG NUMBER column holds the words 'GENERATOR SET', the "
  "same text as the EQUIPMENT NAME column. It does not identify one machine, so it cannot serve "
  "as the join key to the BMS the way every other tag in this workbook does. Ask for the real "
  "asset tag."),
 ("Serial number", "The serial number 11 211 038571-16 is specific to one machine, so this row "
  "does describe a single generator even though its tag does not name one."),
 ("Model", "CTM 4012-46TAG3A is a Perkins 4012-46TAG3A engine badged by CTM. The list states the "
  "manufacturer as CTM; the engine builder was not inferred into the data."),
 ("Date installed", "Given as 'Jun-12' - month and year, no day."),
 ("Deferred fields", "PM procedure, procedure document and recommended spare parts all read "
  "'REFER O&M'. The O&M manual is where those live; nothing was invented for them."),
]

"""Write the plain-English virtual meter decision log, one workbook per building.

Five columns, one row per meter class. The point is that a reader who was not in
the room can see what was built, what was not, and why - so "Reason" carries the
evidence, not a label.
"""
import pathlib
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

ROOT = pathlib.Path('/home/user/claudeskills')
HEAD = ["Meter class", "Tiers", "Meters", "Status", "Reason"]

QNL = [
 ("para:Utility_Meter", "Building", 1, "Built",
  "Measures the incoming municipal supply. QNL_TotalEnergy.Energy is a live physical meter on the same supply - both are kept, because the gap between an imported reading and a calculated roll-up is losses and unmetered load."),
 ("para:SPWR_Meter", "Building + Floor", 6, "Built",
  "Small power (sockets and receptacles), not solar. Ticked on the client's own hand-built matrix. QNL has 0 small-power tags and its 17 SMDB tags are all .TripCtr trip counters carrying no power, so these render empty until a small-power circuit is metered. Kept at client direction."),
 ("para:Common_Util_Meter", "Building + Floor", 6, "Built",
  "Common-area utilities. Depends on MDB, MV, MFM and MCC equipment. Kept at client direction 2026-09-09; which boards feed common areas needs the electrical schedule, which the client does not yet have."),
 ("para:CHW_Meter", "Building + Floor + Room", 360, "Built",
  "Chilled water thermal load. Real inputs exist, and para:contributionFraction on all 299 VAVs and CAVs is what lets an AHU's load be apportioned down to the rooms it serves. Points take para:KiloWt / para:KiloWt-HR, never unit:KiloW, so a building demand roll-up cannot add chilled-water kW to electrical kW."),
 ("para:HVAC_Meter", "Building + Floor + Room", 360, "Built", "HVAC electrical load. Real inputs exist across AHU and pump power tags."),
 ("para:LTG_Meter", "Building + Floor + Room", 360, "Built",
  "Lighting electrical load. NO ENERGY INPUT TODAY - QNL's lighting circuits publish On/Off status and no kW or kWh - so all 360 render empty until a lighting energy tag exists. Kept at client direction 2026-09-09: the calculation will be looked at in future."),
 ("brick:Electrical_Meter", "Building + Floor + Room", 360, "Built", "Total electrical roll-up, summing across UPS, panels and generator. Belongs at every tier, unlike Utility."),
 ("para:UPS_Meter", "Building", 0, "REMOVED 2026-09-09",
  "A UPS meter sums UPS load and QNL publishes no UPS datapoint. Its only UPS evidence is two room names and one false-positive IO tag (QNL_CHW_HEX.PmpStageUpspd, 'Pump Stage Up Speed'). Would have rendered an empty tile. 1 meter, 9 rows removed."),
 ("para:HW_Meter", "Building + Floor", 0, "REMOVED 2026-09-09",
  "Measures DOMESTIC hot water. The equipment exists - the historian carries a calorifier - but it publishes only two alarms and a supply temperature: no power, no energy, no flow, so there is nothing a thermal meter can sum. The calorifier is also outside the agreed selected-datapoint scope. These 6 meters had been summing nothing since the day they were generated. 49 rows removed."),
 ("brick:Water_Meter", "-", 0, "Not built",
  "No potable-water point exists anywhere in the sheet, so the meter would have no input at all."),
 ("para:Occupant-Wellbeing_Meter", "-", 0, "Not built",
  "Needs CO2, TVOC, PM, lux, noise or occupancy points. QNL has none of them."),
]

SSC = [
 ("para:Utility_Meter", "Building", 1, "Built",
  "Measures the incoming municipal supply. Inputs: SSC_MV_InACB, SSC_ELEC_MFM_MV_OG_I3.kW/.kWh and SSC_EnergyConsumptionCalc.kW."),
 ("para:SPWR_Meter", "Building + Floor", 5, "Built",
  "Small power (sockets and receptacles), not solar. 200 SMDB power/energy tags are the candidate inputs; which boards feed small power awaits the electrical schedule, which the client does not yet have. Kept at client direction."),
 ("para:Common_Util_Meter", "Building + Floor", 5, "Built",
  "Common-area utilities, drawing on the same 12 SMDB boards, same pending schedule. Depends on MDB, MV, MFM and MCC equipment, which SSC has. Kept at client direction."),
 ("para:CHW_Meter", "Building + Floor + Room", 171, "Built",
  "Chilled water thermal load. Inputs: SSC_CHWConsumption.KWh plus 20 thermal points on 5 AHUs, 11 FCUs and 4 CHW pumps. para:contributionFraction on all 108 VAVs apportions each AHU's load to the rooms it serves - though only 61 of 166 rooms are VAV-served, so the room tier is real for those and empty for the rest."),
 ("para:HVAC_Meter", "Building + Floor + Room", 171, "Built", "HVAC electrical load. Inputs: 22 AHU kW/kWh, 8 CHW pump and 49 MCC power tags."),
 ("para:LTG_Meter", "Building + Floor + Room", 171, "Built",
  "Lighting electrical load. NO ENERGY INPUT AT ALL - SSC's 55 SSC_LCPB_* lighting circuits are every one an On/Off status with no kW or kWh - so all 171 render empty until a lighting energy tag exists. Built at client direction to match QNL, which is in the same position."),
 ("brick:Electrical_Meter", "Building + Floor + Room", 171, "Built", "Total electrical roll-up. Inputs: 100 SMDB kW, 100 SMDB MWh and 110 MV tags."),
 ("para:UPS_Meter", "Building", 0, "REMOVED 2026-09-09",
  "A UPS meter sums UPS load and SSC publishes no UPS datapoint. Would have rendered an empty tile. 1 meter, 9 rows removed. Note the rooms named UPS keep their own room-tier meters - those are a different thing and were untouched."),
 ("para:HW_Meter", "-", 0, "Never built; declaration removed 2026-09-09",
  "Measures DOMESTIC hot water. SSC's heating is ELECTRIC - 5 AHU heater commands and 14 CRAC heater statuses - and there is no hot-water loop and not one hot-water tag in 5,751 IO rows. No meter was ever generated, but the sheet still carried a dangling para:HW_Meter class declaration with nothing under it; that row was removed."),
 ("Cooling load, AHU and FCU coils and CHW pumps", "Equipment", 18, "Built (delivered, restructured 2026-09-09)",
  "36 cooling load points on 16 cooling valves and 4 CHW booster pumps. Delivered by the client behind an intermediate meter entity; that node was removed so the points hang directly off the coil valve or pump that meters them, and they were retyped to para:Cooling_Thermal_* so cooling and heating are distinguishable."),
 ("Heating load, AHU heating coils", "Equipment", 5, "Added 2026-09-09",
  "SSC's AHUs heat electrically, so the coil's heat output is real thermal power worth metering. 10 points on the 5 brick:Heating_Coil entities. NO INPUT YET: the only heating point is a percent command with no nameplate rating, so these are containers until the AHU heater kW arrives from the datasheets - percent x rating is the whole formula. Tokens HEATPWR_KWT_CALC / HEATPWR_KWHT_CALC are derived, not confirmed: Dar Cairo has no heating token at all."),
 ("Electrical load, FCUs, motors and CHW pumps", "Equipment", 25, "Built (delivered, restructured 2026-09-09)",
  "46 electrical points delivered by the client behind an intermediate meter entity. Those nodes were removed so every meter point in the sheet hangs off the equipment it measures, leaving one convention instead of two."),
]

def write(rows, path, title, subtitle):
    wb = Workbook(); ws = wb.active; ws.title = "Virtual meters"
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = subtitle
    ws["A2"].font = Font(italic=True, color="555555")
    ws.append([]); ws.append(HEAD)
    hdr = ws.max_row
    for c in range(1, len(HEAD) + 1):
        cell = ws.cell(hdr, c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="44546A")
        cell.alignment = Alignment(vertical="center")
    for r in rows:
        ws.append(list(r))
        n = ws.max_row
        status = r[3]
        if status.startswith("REMOVED"):
            fill = "FCE4E4"
        elif status.startswith("Not built") or status.startswith("Never built"):
            fill = "EFEFEF"
        elif status.startswith("Added"):
            fill = "E4F2E4"
        else:
            fill = None
        for c in range(1, len(HEAD) + 1):
            cell = ws.cell(n, c)
            cell.alignment = Alignment(vertical="top", wrap_text=(c == 5))
            if fill:
                cell.fill = PatternFill("solid", fgColor=fill)
    live = [r for r in rows if r[3].startswith(("Built", "Added"))]
    space = sum(r[2] for r in live if r[1] != "Equipment")
    equip = sum(r[2] for r in live if r[1] == "Equipment")
    ws.append([])
    # Space-tier meters and equipment-tier ones are different units and must not
    # be added together - one counts meters, the other counts host assets.
    ws.append(["TOTAL space-tier virtual meters", "", space, "",
               "One meter per (class x space). Matches the ontology exactly."])
    ws.cell(ws.max_row, 1).font = Font(bold=True)
    ws.cell(ws.max_row, 3).font = Font(bold=True)
    if equip:
        ws.append(["Equipment-tier metered assets", "", equip, "",
                   "Counted separately - these are host assets carrying load points, "
                   "not space meters, so the two totals are not addable."])
        ws.cell(ws.max_row, 1).font = Font(bold=True)
        ws.cell(ws.max_row, 3).font = Font(bold=True)
    for col, w in zip("ABCDE", (44, 24, 9, 34, 110)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = ws.cell(hdr + 1, 1)
    ws.auto_filter.ref = f"A{hdr}:E{hdr + len(rows)}"
    wb.save(path)
    print(f"wrote {path}  ({len(rows)} rows, {space} space-tier"
          f"{f', {equip} equipment-tier' if equip else ''})")

write(QNL, ROOT / "projects/QNL/QNL_virtual_meter_log.xlsx",
      "QNL - virtual meter decisions",
      "Why each meter class is in the ontology, or is not. Sheet state 2026-09-09: 1,453 space-tier virtual meters.")
write(SSC, ROOT / "projects/SSC/SSC_virtual_meter_log.xlsx",
      "SSC - virtual meter decisions",
      "Why each meter class is in the ontology, or is not. Sheet state 2026-09-09: 695 space-tier virtual meters, plus the equipment-tier families.")

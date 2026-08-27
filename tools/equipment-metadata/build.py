import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
from ahu import AHU
from ccu import CCU
from climate import CLIMATE
from fcu import FCU_COLS, FCU_ROWS, FCU_NOTES
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from units_map import UNIT_MAP, resolve, convert

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = sys.argv[1]

def _sigfmt(f):
    """Show the factor the way an engineer would check it: 'x 1000' or '/ 3.6'."""
    if f >= 1:
        return "x %g" % f
    return "/ %g" % float("%.6g" % (1 / f))

HEAD = ["Equipment Tag","Model","Component","Property",
        "Value (as printed)","Unit (as printed)",
        "Value (Dar Cairo)","Unit (QUDT)","Conversion",
        "Source File","Page","Note"]

WRAP_COLS = (5, 7, 9, 12)
NOTE_COL, PAGE_COL = 12, 11

def expand(row):
    """9-column source row -> 12-column row carrying the Dar Cairo value and unit."""
    tag, model, comp, prop, val, unit, src, page, note = row
    qudt, factor, in_dc, cnote = resolve(unit, prop)
    if not qudt:
        return [tag, model, comp, prop, val, unit, "", "", cnote, src, page, note]
    new, ok = convert(val, factor)
    if not ok:
        return [tag, model, comp, prop, val, unit, "", "",
                "not converted - value is not numeric", src, page, note]
    bits = []
    if cnote: bits.append(cnote)
    if not in_dc: bits.append("unit not used in Dar Cairo")
    return [tag, model, comp, prop, val, unit, new, qudt, "; ".join(bits), src, page, note]

HDR_FILL   = PatternFill("solid", fgColor="1F3864")
HDR_FONT   = Font(bold=True, color="FFFFFF", size=10)
BAND_FILL  = PatternFill("solid", fgColor="EEF2F8")
COMP_FONT  = Font(bold=True, size=10)
NOTE_FONT  = Font(italic=True, size=9, color="8B4000")
THIN = Side(style="thin", color="C9D2E0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# ---------------------------------------------------------------- AHU
OCTAVES = "63/125/250/500/1k/2k/4k/8k Hz"

FAN_F = [("model","Fan model",""),("impeller","Impeller type",""),
    ("air_flow_m3_s","Air flow","m3/s"),("esp_pa","External static pressure","Pa"),
    ("fsp_pa","Fan static pressure","Pa"),("speed_rpm","Speed","rpm"),
    ("abs_power_kw","Absorbed power","kW"),("swl_db","Sound power level ("+OCTAVES+")","dB"),
    ("volume_control","Volume control",""),("finish","Finish",""),
    ("shaft_guards","Shaft guards",""),("inspection_door","Inspection door",""),
    ("inlet_guards","Inlet guards",""),("ss_shaft","Stainless steel shaft",""),
    ("drain_plug","Drain plug",""),("spark_min","Spark minimising features",""),
    ("avm_type","AVM type",""),("pulley","Fan pulley",""),("note","Note","")]

MOT_F = [("rating_kw","Rating","kW"),("frame_type","Frame type",""),
    ("efficiency_class","Efficiency class",""),("fl_speed_rpm","Full load speed","rpm"),
    ("supply","Supply",""),("flc_a","Full load current","A"),
    ("winding","Winding type",""),("starting_current_a","Starting current","A"),
    ("starting_method","Starting method",""),("thermistor","Thermistor fitted",""),
    ("epoxy_paint","Epoxy paint finish",""),("spare_belts_sets","Spare drive belts","set(s)"),
    ("pulley","Motor pulley",""),("belts","Belts","n"),("belt_type","Belt type","")]

COIL_F = [("model","Model",""),("rows","Rows","n"),("fin_spacing_mm","Fin spacing","mm"),
    ("fins","Fins",""),("tubes","Tubes",""),("conn_supply_bsp","Connection supply","BSP"),
    ("conn_return_bsp","Connection return","BSP"),("water_kg_s","Water flow","kg/s"),
    ("water_pd_kpa","Water pressure drop","kPa"),("total_capacity_kw","Total capacity","kW"),
    ("ent_air_cdb","Entering air (DB)","degC"),("ent_air_rh","Entering air RH","%"),
    ("lvg_air_cdb","Leaving air (DB)","degC"),("lvg_air_rh","Leaving air RH","%"),
    ("ent_water_c","Entering water","degC"),("lvg_water_c","Leaving water","degC"),
    ("glycol_type","Glycol type",""),("glycol_pct","Glycol","%"),
    ("conn_type","Connection type",""),("moisture_eliminator","Moisture eliminator",""),
    ("binder_tapping_points","Binder tapping points",""),("drain_conn_bsp","Drain connection","BSP"),
    ("drain_pan","Drain pan",""),("casing","Casing",""),("note","Note","")]

AUX_F = [("label","Description",""),("air_flow_m3_h","Air flow","m3/h"),
    ("air_mass_flow_kg_s","Air mass flow","kg/s"),("water_flow_l_h","Water flow","l/h"),
    ("water_mass_flow_kg_s","Water mass flow","kg/s"),("ent_water_c","Entering water","degC"),
    ("lvg_water_c","Leaving water","degC"),("water_pd_kpa","Water pressure drop","kPa"),
    ("ent_air_c","Entering air","degC"),("ent_air_rh","Entering air RH","%"),
    ("lvg_air_c","Leaving air","degC"),("lvg_air_rh","Leaving air RH","%"),
    ("air_pd_pa","Air pressure drop","Pa"),("total_capacity_kw","Total capacity","kW"),
    ("tubes","Tubes","")]

ELEC_F = [("supply","Electrical supply",""),("total_capacity_kw","Total capacity","kW"),
    ("stages","Stages","n"),("ent_air_c","Entering air","degC"),
    ("lvg_air_c","Leaving air","degC"),("note","Note","")]

FIN_F = [("frames","Frames",""),("panels_outer","Panels outer skin",""),
    ("panels_inner","Panels inner skin",""),
    ("panels_inner_at_coil","Panels inner skin at coil section",""),
    ("unit_base","Unit base",""),("supply_fan_base","Supply fan base",""),
    ("extract_fan_base","Extract fan base","")]

def fmt(v):
    if isinstance(v, list): return " / ".join(str(x) for x in v)
    return v

def emit(rows, tag, model, comp, fields, data, src, page, note=""):
    for key, label, unit in fields:
        if key in data and data[key] not in (None, ""):
            rows.append([tag, model, comp, label, fmt(data[key]), unit, src, page, note])

def build_ahu(rows):
    for tag in sorted(AHU):
        d = AHU[tag]; src, page = d["src"], d["page"]
        model = d["supply_fan"]["model"] if "supply_fan" in d else ""
        rows.append([tag, "", "Drawing", "Drawing number", d["dwg"], "", src, page, ""])
        rows.append([tag, "", "Drawing", "Sheet", d["sheet"], "", src, page,
                     "AS BUILT general arrangement, Mercury Mena / Qatar Foundation"])
        for i, s in enumerate(d.get("silencers", []), 1):
            c = "Silencer (item %s)" % s["item"]
            rows.append([tag, "", c, "Silencer length", s["length_mm"], "mm", src, page, ""])
            rows.append([tag, "", c, "Insertion loss (%s)" % OCTAVES,
                         fmt(s["insertion_loss_db"]), "dB", src, page,
                         "Tissue faced complete with perforated plate"])
        for f in d.get("filters", []):
            c = "Polyseal filter (item %s) - %s" % (f["item"], f["stage"])
            rows.append([tag, "", c, "Media", f["media"], "", src, page, ""])
            if "arrestance" in f:
                rows.append([tag, "", c, "Arrestance", f["arrestance"], "", src, page, ""])
            if "efficiency" in f:
                rows.append([tag, "", c, "Efficiency", f["efficiency"], "", src, page, ""])
            for pn, dim, off in f["parts"]:
                rows.append([tag, "", c, "Part no %s (W x H x D mm)" % pn, dim, "mm", src, page,
                             "Quantity off: %s" % off])
            rows.append([tag, "", c, "Spare sets", f["spare_sets"], "set(s)", src, page, ""])
        if "cooling_coil" in d:
            emit(rows, tag, "", "Cooling coil", COIL_F, d["cooling_coil"], src, page)
        if "aux_cooling_coil" in d:
            emit(rows, tag, "", "External auxiliary cooling coil", AUX_F, d["aux_cooling_coil"], src, page)
        if "electric_coil" in d:
            emit(rows, tag, "", "Electric coil", ELEC_F, d["electric_coil"], src, page)
        if "supply_fan" in d:
            emit(rows, tag, "", "Supply fan", FAN_F, d["supply_fan"], src, page)
        if "supply_motor" in d:
            emit(rows, tag, "", "Supply fan drive motor", MOT_F, d["supply_motor"], src, page)
        if "return_fan" in d:
            emit(rows, tag, "", "Return fan", FAN_F, d["return_fan"], src, page)
        if "return_motor" in d:
            emit(rows, tag, "", "Return fan drive motor", MOT_F, d["return_motor"], src, page)
        if "flexible_connection" in d:
            rows.append([tag, "", "Flexible connection", "Material", d["flexible_connection"],
                         "", src, page, ""])
        if "finish" in d:
            emit(rows, tag, "", "Finish", FIN_F, d["finish"], src, page)
        if "insulation" in d:
            rows.append([tag, "", "Insulation", "Panels", d["insulation"], "", src, page, ""])
        if "drawing_anomaly" in d:
            rows.append([tag, "", "Data quality", "Drawing anomaly", d["drawing_anomaly"],
                         "", src, page, "Confirm with the supplier before use"])

# ---------------------------------------------------------------- CCU
CCU_LABELS = {
 "design": ("Design condition", {
   "inlet_air_c":("Unit inlet air temperature","degC"),
   "inlet_air_rh":("Unit inlet air relative humidity","%"),
   "airflow_m3_h":("Unit airflow","m3/h"), "esp_pa":("ESP","Pa"),
   "sea_level_m":("Sea level","m"), "refrigerant":("Refrigerant",""),
   "fluid":("Fluid",""), "inlet_fluid_c":("Inlet fluid temperature","degC"),
   "outlet_fluid_c":("Outlet fluid temperature","degC"),
   "unit_fluid_flow_l_s":("Unit fluid flow","l/s"),
   "power_supply":("Unit power supply","")}),
 "performance": ("Unit performance", {
   "total_cooling_kw":("Total cooling capacity","kW"),
   "sensible_cooling_kw":("Sensible cooling capacity","kW"), "shr":("SHR",""),
   "off_coil_air_c":("Off coil air temperature","degC"),
   "off_coil_rh":("Off coil air relative humidity","%"),
   "room_spl_2m_dba":("Room SPL (@ 2 m, f.f)","dB(A)"),
   "condensing_temp_c":("Condensing temperature","degC"),
   "unit_power_input_kw":("Unit power input","kW"), "unit_eer":("Unit EER",""),
   "system_power_input_kw":("System power input","kW"), "system_eer":("System EER",""),
   "filter_class_en779":("Internal filter class (EN779 std)",""),
   "width_mm":("Width","mm"), "depth_mm":("Depth","mm"), "height_mm":("Height","mm"),
   "weight_kg":("Weight","kg")}),
 "cw_coil": ("CW coil", {
   "qty":("Quantity","n"), "unit_fluid_flow_l_s":("Unit fluid flow","l/s"),
   "unit_fluid_side_pd_kpa":("Unit fluid side pressure drop","kPa"),
   "coil_plus_connections_pd_kpa":("Fluid pressure drop coil + connections","kPa"),
   "valve_pd_kpa":("Valve pressure drop","kPa")}),
 "fans": ("Fans", {
   "qty":("Quantity","n"), "type":("Type",""), "power_supply":("Power supply",""),
   "power_input_kw":("Power input","kW"), "operating_a":("Operating ampere","A"),
   "fla_a":("Full load ampere","A"), "lra_a":("Locked rotor amp.","A"),
   "fan_input_voltage_v":("Fan input voltage","V")}),
 "compressors": ("Compressors", {
   "qty":("Quantity","n"), "power_supply":("Power supply",""),
   "power_input_kw":("Power input","kW"), "cop":("Compressors COP",""),
   "operating_a":("Operating ampere","A"), "fla_a":("Full load ampere","A"),
   "lra_a":("Locked rotor amp.","A")}),
 "condenser": ("Condenser", {
   "model":("Condenser model",""), "version":("Version",""),
   "air_discharge":("Air discharge",""), "power_supply":("Power supply",""),
   "variex":("Variex",""), "heat_load_kw":("Heat load","kW"),
   "outdoor_air_c":("Outdoor air temperature","degC"),
   "airflow_max_m3_h":("Condenser airflow (@ max speed)","m3/h"),
   "actual_airflow_m3_h":("Condenser actual airflow","m3/h"),
   "esp_pa":("Condenser ESP (@ max speed)","Pa"),
   "max_outdoor_spl_5m_dba":("Max outdoor SPL (@ 5 m, f.f.)","dB(A)"),
   "actual_outdoor_spl_5m_dba":("Actual outdoor SPL (@ 5 m, f.f.)","dB(A)"),
   "power_input_kw":("Power input","kW"), "fla_a":("Full load ampere","A"),
   "lra_a":("Locked rotor amp.","A"), "width_mm":("Width","mm"),
   "depth_mm":("Depth","mm"), "height_mm":("Height","mm"), "weight_kg":("Weight","kg"),
   "note":("Note","")}),
 "electric_reheat": ("Option - electrical re-heating", {
   "label":("Sheet heading",""), "max_capacity_kw":("Max re-heating capacity","kW"),
   "fla_a":("FLA","A"), "inlet_air_c":("Inlet air temperature","degC"),
   "inlet_air_rh":("Inlet air relative humidity","%"),
   "outlet_air_c":("Outlet air temperature","degC"),
   "outlet_air_rh":("Outlet air relative humidity","%")}),
 "humidifier": ("Option - humidifier", {
   "qty":("Quantity","n"), "max_steam_kg_h":("Max capacity steam","kg/h"),
   "min_steam_kg_h":("Min capacity steam","kg/h"), "type":("Type of humidifier",""),
   "power_supply":("Power supply",""), "nominal_power_input_kw":("Nominal power input","kW"),
   "max_absorption_a":("Max absorption current","A")}),
}

def build_ccu(rows):
    for tag, d in CCU.items():
        src = d["src"]; pp = d["pages_perf"]; po = d["pages_options"]
        model = d["model"]
        rows.append([tag, model, "Identification", "Manufacturer", d["manufacturer"], "", src, pp, ""])
        rows.append([tag, model, "Identification", "Model", model, "", src, pp, ""])
        rows.append([tag, model, "Identification", "System type", d["system_type"], "", src, pp, ""])
        rows.append([tag, model, "Identification", "Issued by", d["issued_by"], "", src, pp, ""])
        rows.append([tag, model, "Identification", "Selection date", d["selection_date"], "", src, pp, ""])
        rows.append([tag, model, "Identification", "Selection software release",
                     d["software_rel"], "", src, pp, ""])
        if "pages_dimension_drawing" in d:
            rows.append([tag, model, "Identification", "Dimension drawing pages",
                         d["pages_dimension_drawing"], "", src, d["pages_dimension_drawing"], ""])
        for key, (comp, labels) in CCU_LABELS.items():
            if key not in d: continue
            page = po if key in ("electric_reheat", "humidifier") else pp
            blk = d[key]
            for f, val in blk.items():
                if f not in labels: continue
                label, unit = labels[f]
                rows.append([tag, model, comp, label, val, unit, src, page, ""])
        if "compliance" in d:
            rows.append([tag, model, "Compliance", "Declared performance / directives",
                         d["compliance"], "", src, pp, ""])
        if "note" in d:
            rows.append([tag, model, "Note", "Sheet note", d["note"], "", src, pp, ""])
        if "source_anomaly" in d:
            rows.append([tag, model, "Data quality", "Source anomaly", d["source_anomaly"],
                         "", src, pp, "Confirm with the supplier before use"])

# ---------------------------------------------------------------- Climate
def build_climate(rows):
    for tag, d in CLIMATE.items():
        src, page = d["src"], d["page"]
        model = d["model"]
        rows.append([tag, model, "Identification", "Manufacturer", d["manufacturer"], "", src, page, ""])
        rows.append([tag, model, "Identification", "Model", model, "", src, page, ""])
        rows.append([tag, model, "Identification", "Equipment type", d["equipment_type"], "", src, page, ""])
        if "doc_status" in d:
            rows.append([tag, model, "Identification", "Document status", d["doc_status"], "", src, page, ""])
        for block, comp in (("specifications","Specifications"), ("technical_data","Technical data")):
            for f, v in d.get(block, {}).items():
                unit = ""
                lbl = f.replace("_"," ").capitalize()
                for suf, u in (("_kw","kW"),("_kg","kg"),("_mm","mm"),("_a","A"),("_w","W"),
                               ("_rpm","rpm"),("_v_dc","V DC"),("_dba","dB(A)"),
                               ("_mbar","mbar"),("_hours","hours"),("_lb","lb"),("_c","degC")):
                    if f.endswith(suf):
                        unit = u; lbl = f[:-len(suf)].replace("_"," ").capitalize(); break
                rows.append([tag, model, comp, lbl, v, unit, src, page, ""])
        for f, v in d.get("dimensions_mm", {}).items():
            # "mounting" is a screw specification (8 x M4 x 6), not a length
            unit = "" if f == "mounting" else "mm"
            rows.append([tag, model, "Dimensions", f.replace("_"," ").capitalize(),
                         v, unit, src, page, ""])
        for key, comp in (("installation_requirements","Installation requirement"),
                          ("systems_included","System included"),
                          ("features","Feature"),
                          ("stages",None)):
            v = d.get(key)
            if isinstance(v, list):
                for i, item in enumerate(v, 1):
                    rows.append([tag, model, comp, "%s %d" % (comp, i), item, "", src, page, ""])
            elif isinstance(v, dict):
                for f, item in v.items():
                    rows.append([tag, model, "Filtration stages",
                                 f.capitalize(), item, "", src, page, ""])
        for key, comp in (("installation","Installation"), ("control_wiring","Control wiring")):
            blk = d.get(key)
            if not blk: continue
            pg = blk.get("page", page)
            for f, v in blk.items():
                if f == "page": continue
                rows.append([tag, model, comp, f.replace("_"," ").capitalize(), v, "", src, pg, ""])
        for f, comp in (("designed_for","Application"), ("options","Options"),
                        ("warranty","Warranty"), ("note","Note")):
            if f in d:
                rows.append([tag, model, comp, comp, d[f], "", src, page, ""])
        if "dimension_drawings" in d:
            dd = d["dimension_drawings"]
            for f, v in dd.items():
                if f == "pages": continue
                unit, lbl = "", f.replace("_"," ").capitalize()
                if f.endswith("_mm"):
                    unit, lbl = "mm", f[:-3].replace("_"," ").capitalize()
                rows.append([tag, model, "Dimension drawing", lbl, v, unit, src, dd["pages"], ""])
        if "source_conflict" in d:
            rows.append([tag, model, "Data quality", "Source conflict", d["source_conflict"],
                         "", src, page, "Confirm with the manufacturer before use"])

# ---------------------------------------------------------------- FCU
FCU_LABEL = {
 "total_cooling_kw":("Capacity","Total capacity (cooling)","kW"),
 "sensible_cooling_kw":("Capacity","Sensible capacity (cooling)","kW"),
 "condensed_water_g_h":("Capacity","Condensed water","g/h"),
 "rows_n":("Coil","Rows","n"),
 "air_in_dbt_c":("Air","Inlet DBT","degC"),
 "air_in_wbt_c":("Air","Inlet WBT","degC"),
 "air_in_rh_pct":("Air","Inlet RH","%"),
 "air_out_dbt_c":("Air","Outlet DBT","degC"),
 "air_out_wbt_c":("Air","Outlet WBT","degC"),
 "air_out_rh_pct":("Air","Outlet RH","%"),
 "air_flow_m3_h":("Air","Flow rate","m3/h"),
 "fan_speed":("Air","Fan speed setting",""),
 "air_velocity_m_s":("Air","Air velocity","m/s"),
 "air_pressure_drop_pa":("Air","Air pressure drop","Pa"),
 "fluid_flow_l_h":("Fluid","Flow rate","l/h"),
 "fluid_pd_kpa":("Fluid","Pressure drop","kPa"),
 "fluid_in_c":("Fluid","Inlet temperature","degC"),
 "fluid_out_c":("Fluid","Outlet temperature","degC"),
 "fluid":("Fluid","Fluid",""),
 "max_width_mm":("Dimensions and weight","Max width","mm"),
 "max_height_mm":("Dimensions and weight","Max height","mm"),
 "max_thickness_mm":("Dimensions and weight","Max thickness","mm"),
 "weight_kg":("Dimensions and weight","Weight","kg"),
 "power_supply":("Other data","Power supply","V-ph-Hz"),
 "max_absorbed_power_w":("Other data","Max. absorbed power","W"),
 "max_absorbed_current_a":("Other data","Max. absorbed current","A"),
 "sound_pressure_dba":("Other data","Sound pressure level","dB(A)"),
 "sound_power_dba":("Other data","Sound power level","dB(A)"),
 "static_pressure_pa":("Other data","Static pressure","Pa"),
}
SRC_FCU = "FCU_Manual.pdf"

def build_fcu(rows):
    idx = {c: i for i, c in enumerate(FCU_COLS)}
    for r in FCU_ROWS:
        tag = r[idx["position"]]; page = r[idx["page"]]; model = r[idx["model"]]
        rows.append([tag, model, "Identification", "Manufacturer",
                     "Euroclima AG/Spa-Ges.m.b.H", "", SRC_FCU, page, ""])
        rows.append([tag, model, "Identification", "Offer", r[idx["offer"]], "", SRC_FCU, page, ""])
        rows.append([tag, model, "Identification", "Range", r[idx["range"]], "", SRC_FCU, page, ""])
        rows.append([tag, model, "Identification", "Version", r[idx["version"]], "", SRC_FCU, page, ""])
        rows.append([tag, model, "Identification", "Model", model, "", SRC_FCU, page, ""])
        for c, (comp, label, unit) in FCU_LABEL.items():
            v = r[idx[c]]
            if v is None: continue
            note = ""
            if c == "air_pressure_drop_pa" and tag != "FCU/B/01":
                note = ("Row printed as 'Perdita di carico aria [degC]' on this sheet - "
                        "untranslated label with the wrong unit; the value is Pa.")
            rows.append([tag, model, comp, label, v, unit, SRC_FCU, page, note])
        rows.append([tag, model, "Capacity", "Heating capacity", "-", "kW", SRC_FCU, page,
                     "Heating column blank on the sheet; cooling-only selection."])
        if tag in FCU_NOTES:
            rows.append([tag, model, "Data quality", "Sheet note", FCU_NOTES[tag], "", SRC_FCU, page,
                         "Confirm with the supplier before use"])

# ---------------------------------------------------------------- write
def sheet(wb, name, rows, subtitle):
    rows = [expand(r) for r in rows]
    ws = wb.create_sheet(name)
    ws["A1"] = name; ws["A1"].font = Font(bold=True, size=14, color="1F3864")
    ws["A2"] = subtitle; ws["A2"].font = Font(italic=True, size=9, color="555555")
    ws.append([])
    ws.append(HEAD)
    hr = ws.max_row
    for c in range(1, len(HEAD)+1):
        cell = ws.cell(row=hr, column=c)
        cell.fill = HDR_FILL if c not in (7, 8, 9) else PatternFill("solid", fgColor="2E5F2E")
        cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    tags = []
    for r in rows:
        ws.append(r); tags.append(r[0])
    order, seen = [], set()
    for t in tags:
        if t not in seen: seen.add(t); order.append(t)
    band = {t: (i % 2 == 1) for i, t in enumerate(order)}
    for i, r in enumerate(rows):
        rr = hr + 1 + i
        for c in range(1, len(HEAD)+1):
            cell = ws.cell(row=rr, column=c)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=(c in WRAP_COLS))
            if band[r[0]]: cell.fill = BAND_FILL
        ws.cell(row=rr, column=1).font = COMP_FONT if (i == 0 or rows[i-1][0] != r[0]) else Font(size=10)
        if r[NOTE_COL-1]: ws.cell(row=rr, column=NOTE_COL).font = NOTE_FONT
        if r[8]: ws.cell(row=rr, column=9).font = Font(italic=True, size=9, color="2E5F2E")
        ws.cell(row=rr, column=PAGE_COL).alignment = Alignment(horizontal="center", vertical="top")
    widths = [16, 24, 28, 40, 20, 13, 20, 20, 30, 32, 7, 50]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=hr+1, column=1)
    ws.auto_filter.ref = "A%d:%s%d" % (hr, get_column_letter(len(HEAD)), ws.max_row)
    return ws

wb = Workbook(); wb.remove(wb.active)

# README
ws = wb.create_sheet("README")
def put(r, a, b="", bold=False, size=10, color="000000", italic=False):
    ws.cell(row=r, column=1, value=a).font = Font(bold=bold, size=size, color=color, italic=italic)
    if b != "":
        c = ws.cell(row=r, column=2, value=b)
        c.font = Font(size=10); c.alignment = Alignment(wrap_text=True, vertical="top")

put(1, "QNL Equipment Metadata - Manufacturer Properties", bold=True, size=16, color="1F3864")
put(2, "Qatar National Library, Education City BP#7A", italic=True, color="555555")
r = 4
put(r, "What this workbook is", bold=True, size=12, color="1F3864"); r += 1
put(r, "", "One sheet per equipment type. Every row is a single manufacturer property for a single "
          "unit, and carries the source PDF and the page it was read from, so any value can be "
          "traced back to the document."); r += 2
put(r, "Sheets", bold=True, size=12, color="1F3864"); r += 1
for name, desc in [
  ("AHU", "15 air handling units, AHU-001 to AHU-015. AS BUILT general arrangement drawings, "
          "drawing 1844-SD-05-AC-0077, Mercury Mena for Qatar Foundation, 26-10-2015 / 28-11-2015."),
  ("Closed Control Units", "5 selection sheets covering CC/B/01 to CC/B/09. Emerson Network Power, "
          "issued by Qatar Site & Power, April and October 2013."),
  ("Climate Control Units", "Museum Climate Controls MCG-10P humidity control unit with its VCB1000 "
          "blower option and AF4 intake air filter."),
  ("FCU", "28 Euroclima selection sheets covering positions on Basement, 1F and 2F."),
  ("Units", "Every source unit, the Dar Cairo unit it maps to, the factor applied, and whether "
            "Dar Cairo uses that unit at all."),
]:
    ws.cell(row=r, column=1, value=name).font = Font(bold=True, size=10)
    c = ws.cell(row=r, column=2, value=desc); c.font = Font(size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top"); r += 1
r += 1
put(r, "Columns", bold=True, size=12, color="1F3864"); r += 1
for name, desc in [
  ("Equipment Tag", "The position or unit reference exactly as the source document writes it."),
  ("Model", "Manufacturer model designation where the sheet gives one."),
  ("Component", "The part of the unit the property belongs to - cooling coil, supply fan, condenser, etc."),
  ("Property", "The property name, kept close to the source wording."),
  ("Value (as printed)", "The value exactly as the document prints it. Nothing converted, rounded or inferred."),
  ("Unit (as printed)", "The unit exactly as the document prints it."),
  ("Value (Dar Cairo)", "The same quantity converted to the unit Dar Cairo uses for it."),
  ("Unit (QUDT)", "The QUDT unit token to write into brick:hasUnit."),
  ("Conversion", "The arithmetic applied, and any assumption behind it. Blank means no conversion was needed."),
  ("Source File", "The PDF the value came from."),
  ("Page", "The page of that PDF, 1-based."),
  ("Note", "Anything that qualifies the value - a quantity off, a source conflict, a mislabelled row."),
]:
    ws.cell(row=r, column=1, value=name).font = Font(bold=True, size=10)
    c = ws.cell(row=r, column=2, value=desc); c.font = Font(size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top"); r += 1
r += 1
put(r, "Units", bold=True, size=12, color="2E5F2E"); r += 1
for line in [
  "The source documents are transcribed in their own units, and each row then carries the same "
  "quantity in the unit Dar Cairo uses for it. Both are kept side by side: the printed pair stays "
  "traceable to the page, the converted pair is what goes into brick:hasUnit.",
  "Targets were read off DarCairo_V93.csv, not assumed. Air flow and water flow both land on "
  "unit:L-PER-SEC (para:ratedSupplyAirFlowrate, para:ratedChilledWaterFlowrate and their siblings), "
  "power on unit:KiloW (brick:ratedPowerInput, brick:coolingCapacity), length on unit:M "
  "(para:ratedHead), relative humidity on unit:PERCENT_RH rather than unit:PERCENT.",
  "The Units sheet lists every mapping, the factor applied, and the four QUDT units Dar Cairo has "
  "never used - mass, mass flow and velocity, which it carries no quantity for. Those need the "
  "PARA team's confirmation.",
  "Converting kg/s to l/s treats water as 1 kg/l. At 7-15 degC it is about 0.9997 kg/l, so the "
  "converted flow is high by roughly 0.03%.",
]:
    c = ws.cell(row=r, column=2, value="- " + line); c.font = Font(size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top"); r += 1
r += 1
put(r, "Read before using the data", bold=True, size=12, color="C00000"); r += 1
for line in [
  "Values are transcribed from the documents as printed. Where a document contradicts itself the "
  "conflict is recorded as a 'Data quality' row rather than resolved - those need the supplier's answer.",
  "AHU-011 carries two Item 3 ELECTRIC COIL blocks; the first is an unfilled template "
  "(capacity POW, stages NST, entering air AON, leaving air AOF). The populated block is the one recorded.",
  "MCG-10P size is given as 500 x 650 x 650 mm on the specification sheet and 475 x 430 x 400 mm on "
  "dimension drawing MCG10P-1. Both are recorded; neither is confirmed.",
  "On 27 of the 28 Euroclima sheets the air pressure drop row is printed as 'Perdita di carico aria' "
  "with the unit [degC]. It is air-side pressure drop in Pa - page 2 labels the same row correctly.",
  "The CC/B/05,06,07 sheet heading reads M5DUA while its own Unit row reads M5DOA.",
  "These are equipment selection and as-built documents, not nameplate photographs. Where the "
  "installed plant differs from the selection, the installed plant governs.",
]:
    c = ws.cell(row=r, column=2, value="- " + line); c.font = Font(size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top"); r += 1
r += 1
put(r, "Source documents", bold=True, size=12, color="1F3864"); r += 1
for f, pages, what in [
  ("Ahu_manual_1.pdf", "8 pages", "AHU-001 to AHU-008 general arrangement drawings"),
  ("ahu_2.pdf", "7 pages", "AHU-009 to AHU-015 general arrangement drawings"),
  ("qnl_closed_control_units_manual.pdf", "17 pages", "Emerson closed control unit selections"),
  ("climate_control_units_manual.pdf", "7 pages", "Museum Climate Controls MCG-10P data sheets"),
  ("FCU_Manual.pdf", "29 pages", "Euroclima fan coil unit selection sheets"),
]:
    ws.cell(row=r, column=1, value=f).font = Font(bold=True, size=10)
    c = ws.cell(row=r, column=2, value="%s - %s" % (pages, what)); c.font = Font(size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top"); r += 1
ws.column_dimensions["A"].width = 40
ws.column_dimensions["B"].width = 108
ws.sheet_view.showGridLines = False

rows = []; build_ahu(rows)
sheet(wb, "AHU", rows,
      "Air handling units AHU-001 to AHU-015 - AS BUILT general arrangement drawings, drawing "
      "1844-SD-05-AC-0077 (Mercury Mena for Qatar Foundation). The drawings give no unit-level model "
      "designation, so Model is blank; component models (coil, fan, motor) appear as their own rows.")
n_ahu = len(rows)

rows = []; build_ccu(rows)
sheet(wb, "Closed Control Units", rows,
      "Emerson Network Power closed control units CC/B/01 to CC/B/09 - selection sheets "
      "issued by Qatar Site & Power.")
n_ccu = len(rows)

rows = []; build_climate(rows)
sheet(wb, "Climate Control Units", rows,
      "Museum Climate Controls MCG-10P positive-pressure humidity control unit, "
      "VCB1000 blower option and AF4 intake air filter.")
n_cli = len(rows)

rows = []; build_fcu(rows)
sheet(wb, "FCU", rows,
      "Euroclima fan coil units - one selection sheet per position, offer CENTRAL LIBRARY. Positions "
      "carrying several tags on one sheet (e.g. B/06,08,17,24) were annotated by hand on the printed "
      "sheet; those tags share the selection above them. The Heating column is blank on all 28 sheets.")
n_fcu = len(rows)

# ---------------------------------------------------------------- Units sheet
uw = wb.create_sheet("Units")
uw["A1"] = "Units"; uw["A1"].font = Font(bold=True, size=14, color="1F3864")
uw["A2"] = ("Source unit to Dar Cairo unit. Targets read off reference-models/DarCairo_V93.csv - "
            "air and water flow both land on unit:L-PER-SEC, power on unit:KiloW, length on unit:M.")
uw["A2"].font = Font(italic=True, size=9, color="555555")
uw.append([])
UHEAD = ["Unit (as printed)", "Unit (QUDT)", "Factor applied",
         "Used in Dar Cairo", "Dar Cairo uses (rows)", "Note"]
uw.append(UHEAD)
uhr = uw.max_row
for c in range(1, len(UHEAD)+1):
    cell = uw.cell(row=uhr, column=c)
    cell.fill = HDR_FILL; cell.font = HDR_FONT
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER

DC_USES = {  # usage counts from references/data/units.csv
 "unit:KiloW":1593, "unit:DEG_C":883, "unit:M2":755, "unit:PERCENT":708, "unit:HR":613,
 "unit:L-PER-SEC":535, "unit:V":451, "unit:A":227, "unit:PA":172, "unit:DeciB":171,
 "unit:PERCENT_RH":79, "unit:HZ":61, "unit:M":47, "unit:RPM":21, "unit:W":13,
 "unit:UNITLESS":3376,
}

urows = []
for srcu, (qudt, factor, in_dc, note) in UNIT_MAP.items():
    if srcu == "":
        continue
    urows.append([srcu, qudt or "(none)",
                  "" if factor is None else ("x 1" if factor == 1.0 else _sigfmt(factor)),
                  "yes" if (in_dc and qudt) else ("n/a" if not qudt else "NO"),
                  DC_USES.get(qudt, "" if qudt else ""),
                  note])
urows.append(["%", "unit:PERCENT_RH", "x 1", "yes", DC_USES["unit:PERCENT_RH"],
              "used when the property is a relative humidity"])
urows.append(["%", "unit:PERCENT", "x 1", "yes", DC_USES["unit:PERCENT"],
              "used for every other percentage"])
urows.append(["(none printed)", "unit:UNITLESS", "x 1", "yes", DC_USES["unit:UNITLESS"],
              "dimensionless ratios - SHR, EER, COP, fan speed setting"])
for r_ in urows:
    uw.append(r_)
for i in range(len(urows)):
    rr = uhr + 1 + i
    for c in range(1, len(UHEAD)+1):
        cell = uw.cell(row=rr, column=c)
        cell.border = BORDER
        cell.alignment = Alignment(vertical="top", wrap_text=(c == 6),
                                   horizontal="center" if c in (3, 4, 5) else "left")
    if uw.cell(row=rr, column=4).value == "NO":
        for c in range(1, len(UHEAD)+1):
            uw.cell(row=rr, column=c).fill = PatternFill("solid", fgColor="FFF2CC")
for i, w in enumerate([20, 26, 16, 18, 20, 62], 1):
    uw.column_dimensions[get_column_letter(i)].width = w
uw.freeze_panes = uw.cell(row=uhr+1, column=1)
rr = uw.max_row + 2
uw.cell(row=rr, column=1, value="Highlighted rows are QUDT units Dar Cairo has never used - it "
        "carries no mass, mass-flow or velocity quantity. They are genuine QUDT terms, not minted "
        "ones, but the PARA team should confirm them before handover.").font = NOTE_FONT
uw.cell(row=rr, column=1).alignment = Alignment(wrap_text=True, vertical="top")
uw.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=6)
uw.sheet_view.showGridLines = False

wb.save(OUT)
print("saved", OUT)
print("AHU %d rows | CCU %d | Climate %d | FCU %d | total %d"
      % (n_ahu, n_ccu, n_cli, n_fcu, n_ahu+n_ccu+n_cli+n_fcu))

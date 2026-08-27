#!/usr/bin/env python3
"""Building- and system-level instrumentation for QNL (assumption QNL-024).

The 68 historian tags that sit under a family prefix but are single building- or
system-level measurements, not equipment units. Each is attached to the parent
its Dar Cairo / QF SSC counterpart uses:

  * CHW plant instrumentation -> the chilled-water loop, with a
    Building_Chilled_Water_Meter sub-part for the energy points, exactly as Dar
    Cairo hangs them off entity:CHWS-MAIN-LOOP and its ..._Energy-Meter.
  * Electrical metering -> a brick:Electrical_Meter entity per meter under the
    electrical system, as both Dar Cairo (1,456 Electrical_Meter) and SSC (46)
    model electrical measurement; the building total is a para:Utility_Meter.
  * DX_RP21 and CR_DX_EWRC500 -> orphan DX units (para:DXUnit), the roof/control
    DX the register omits, treated like the other orphans.
  * Loose room/space sensors and group statuses/setpoints with no equipment ->
    orphan points isPartOf the HVAC system, like the CCU room sensors.

Every point carries a label, a mapped unit and a ref:TimeseriesReference on the
point. Classes are assigned explicitly here - this file IS the ledger for these
tags - each traceable to a Dar Cairo/SSC/Brick precedent.
"""

# Chilled-water loop sensors -> hang on the loop entity directly (Dar Cairo puts
# loop temps, pressures and flows on entity:CHWS-MAIN-LOOP / CHWS-LOOP-2).
CHW_LOOP_SENSORS = {
    "QNL_CHW_BldgAvgSupTemp.PV": "brick:Chilled_Water_Supply_Temperature_Sensor",
    "QNL_CHW_BldgSupTemp.PV": "brick:Chilled_Water_Supply_Temperature_Sensor",
    "QNL_CHW_BldgRtnTemp.PV": "brick:Chilled_Water_Return_Temperature_Sensor",
    "QNL_CHW_PriSupTemp.PV": "brick:Chilled_Water_Supply_Temperature_Sensor",
    "QNL_CHW_PriRtnTemp.PV": "brick:Chilled_Water_Return_Temperature_Sensor",
    "QNL_CHW_BldgSupPrs.PV": "brick:Water_Pressure_Sensor",
    "QNL_CHW_BldgRtnPrs.PV": "brick:Water_Pressure_Sensor",
    "QNL_CHW_BldgDiffPrs.PV": "brick:Differential_Pressure_Sensor",
    "QNL_CHW_PriDiffPrs.PV": "brick:Differential_Pressure_Sensor",
    "QNL_CHW_PlantRm1DiffPrs.PV": "brick:Differential_Pressure_Sensor",
    "QNL_CHW_PlantRm2DiffPrs.PV": "brick:Differential_Pressure_Sensor",
    "QNL_CHW_PlantRm3DiffPrs.PV": "brick:Differential_Pressure_Sensor",
    "QNL_CHW_PlantRm4DiffPrs.PV": "brick:Differential_Pressure_Sensor",
    "QNL_CHW_BldgFlow.PV": "brick:Water_Flow_Sensor",
    "QNL_CHW_CHWWtrFlow.PV": "brick:Water_Flow_Sensor",
    "QNL_CHW_DistFlow.PV": "brick:Water_Flow_Sensor",
}
# Energy/power -> a Building_Chilled_Water_Meter sub-part of the loop (Dar Cairo
# entity:CHWS-MAIN-LOOP_Energy-Meter).
CHW_METER_POINTS = {
    "QNL_CHW_CHWEnergy.PV": "brick:Thermal_Energy_Usage_Sensor",
    "QNL_CHW_PriEnergy.PV": "brick:Thermal_Power_Sensor",
    "QNL_CHW_SecEnergy.PV": "brick:Thermal_Power_Sensor",
    "QNL_CHW_HEX.EnergyBTU": "brick:Thermal_Power_Sensor",
    "QNL_CHW_HEX.kW": "brick:Thermal_Power_Sensor",
    "QNL_CHWConsumption.KW": "brick:Thermal_Power_Sensor",
    "QNL_HEX_BldgUtilEnergy.PV": "brick:Thermal_Power_Sensor",
}

# Orphan DX units the register omits (para:DXUnit, isPartOf HVAC).
DX_RP21 = {
    "QNL_DX_RP21_RmTemp.PV": "para:Room_Air_Temperature",
    "QNL_DX_RP21_RmTempSP.SP": "brick:Room_Air_Temperature_Setpoint",
    "QNL_DX_RP21_RmTempSPHys.SP": "para:Room_Air_Temperature_Setpoint_Hysteresis",
    "QNL_DX_RP21_NoOfReqUnits.PV": "para:Required_Units_Count",
    "QNL_DX_RP21_StgUpdly.SP": "para:Stage_Up_Delay_Setpoint",
    "QNL_DX_RP2124_ChOverHrsSP.SP": "para:Changeover_Hours_Setpoint",
}
CR_DX = {
    "QNL_CR_DX_EWRC500.Temp": "brick:Temperature_Sensor",
    "QNL_CR_DX_EWRC500.TempSP": "brick:Temperature_Setpoint",
}

# Electrical meters: one brick:Electrical_Meter per meter, isPartOf the electrical
# system, .kWh -> Electrical_Energy_Usage_Sensor, .KW -> Electric_Power_Sensor.
ELEC_METERS = [
    "QNL_ELEC_MFM_MVP1", "QNL_ELEC_MFM_MVP2", "QNL_ELEC_MFM_MVP3",
    "QNL_ELEC_MFM_Total",
    "QNL_ELEC_MV1_ACB1_MFM", "QNL_ELEC_MV1_ACB2_MFM",
    "QNL_ELEC_MV2_ACB10_MFM", "QNL_ELEC_MV2_ACB11_MFM", "QNL_ELEC_MV3_ACB13_MFM",
    "QNL_ELEC_VCB_11KVIF1_Meter", "QNL_ELEC_VCB_11KVIF2_Meter",
    "QNL_ELEC_VCB_11KVOF1_Meter", "QNL_ELEC_VCB_11KVOF2_Meter",
    "QNL_ELEC_VCB_11KVOF3_Meter",
]

def _elec_point_class(tag):
    low = tag.rsplit(".", 1)[-1].lower()
    return ("brick:Electrical_Energy_Usage_Sensor" if low in ("kwh",)
            else "brick:Electric_Power_Sensor")

# Loose orphan points - the entity IS the point, isPartOf HVAC (like the CCU
# room sensors). No equipment parent is known.
POINT_ORPHANS = {
    "QNL_CPNL2_CCU_SpcHumd.PV": "brick:Relative_Humidity_Sensor",
    "QNL_CPNL2_CCU_SpcTemp.PV": "brick:Temperature_Sensor",
    "QNL_MF_B01_SpcTemp.PV": "brick:Temperature_Sensor",
    "QNL_TEF_B01.LocSts": "para:Local_Status",
    "QNL_TEF_B02.LocSts": "para:Local_Status",
    "QNL_TEF_B03.LocSts": "para:Local_Status",
    "QNL_DX_B0102_ChOverHrsSP.SP": "para:Changeover_Hours_Setpoint",
    "QNL_DX_B030414_ChOverHrsSP.SP": "para:Changeover_Hours_Setpoint",
    "QNL_DX_B0506_ChOverHrsSP.SP": "para:Changeover_Hours_Setpoint",
    "QNL_DX_B0716_ChOverHrsSP.SP": "para:Changeover_Hours_Setpoint",
    "QNL_DX_B0809_ChOverHrsSP.SP": "para:Changeover_Hours_Setpoint",
}

# One breaker point on the existing generator, modelled as a part like ACB14.
GEN_ACB3 = {"QNL_Elec_Gen_ACB3.Alm": "brick:Communication_Loss_Alarm"}

# para: classes these tags introduce, with a Brick parent, for declaration.
PARA_DECL = {
    "para:Required_Units_Count": ("brick:Point", "Required Units Count"),
    "para:Stage_Up_Delay_Setpoint": ("brick:Setpoint", "Stage Up Delay Setpoint"),
    "para:Utility_Meter": ("brick:Electrical_Meter", "Utility Meter"),
}


def build(out, row, label, to_unit, historian,
          HVAC, HVAC_CLASS, CHW, CHW_CLASS, ELEC, ELEC_CLASS,
          LOOP, LOOP_CLASS, declared):
    """Emit all instrumentation rows into `out`. Returns (n_rows, para_used)."""
    n0 = len(out)
    para_used = {}

    def note_para(cls):
        if cls.startswith("para:"):
            para_used[cls] = PARA_DECL.get(cls, (None, None))[0]

    def point_on(owner_id, owner_cls, tag, pcls):
        if tag not in historian:
            return
        pid = "entity:" + tag.replace(".", "_")
        unit = to_unit(historian[tag].get("unit", ""))
        bare = owner_id.replace("entity:", "")
        local = tag[len(bare):].lstrip("_.") if tag.startswith(bare) else tag
        out.append(row(owner_id, owner_cls, "brick:hasPoint", pid, pcls,
                       [("o", "rdfs:label_en", label(local.replace(".", "_"))),
                        ("o", "brick:hasUnit", unit)]))
        out.append(row(pid, pcls, "ref:hasExternalReference", "<blanknode>",
                       "ref:TimeseriesReference",
                       [("o", "ref:hasTimeseriesId", tag),
                        ("o", "para:hasEntityId", tag)]))
        note_para(pcls)

    def declare_owner(owner_id, owner_cls, system, syscls, ifc=True):
        out.append(row(owner_id, owner_cls, "brick:isPartOf", system, syscls,
                       [("s", "rdfs:label_en", label(owner_id.replace("entity:", "")))]))
        if ifc:
            bare = owner_id.replace("entity:", "")
            out.append(row(owner_id, owner_cls, "ref:hasExternalReference",
                           "<blanknode>", "ref:IFCReference",
                           [("o", "para:IFC_ID", ""), ("o", "ref:ifcName", bare)]))
        note_para(owner_cls)

    # 1. CHW loop sensors on the existing loop entity (no re-declaration).
    for tag, pcls in CHW_LOOP_SENSORS.items():
        point_on(LOOP, LOOP_CLASS, tag, pcls)

    # 2. CHW energy meter, a Building_Chilled_Water_Meter part of the loop.
    meter = LOOP + "_Energy-Meter"
    mcls = "brick:Building_Chilled_Water_Meter"
    out.append(row(LOOP, LOOP_CLASS, "brick:hasPart", meter, mcls,
                   [("o", "rdfs:label_en", label(meter.replace("entity:", "")))]))
    for tag, pcls in CHW_METER_POINTS.items():
        point_on(meter, mcls, tag, pcls)

    # 3. Orphan DX units.
    for owner, tags in (("entity:QNL_DX_RP21", DX_RP21),
                        ("entity:QNL_CR_DX_EWRC500", CR_DX)):
        declare_owner(owner, "para:DXUnit", HVAC, HVAC_CLASS)
        for tag, pcls in tags.items():
            point_on(owner, "para:DXUnit", tag, pcls)

    # 4. Electrical meters.
    import collections
    by_meter = collections.defaultdict(list)
    for m in ELEC_METERS:
        for tag in historian:
            if tag.startswith(m + "."):
                by_meter[m].append(tag)
    for m in ELEC_METERS:
        owner = "entity:" + m
        declare_owner(owner, "brick:Electrical_Meter", ELEC, ELEC_CLASS)
        for tag in sorted(by_meter[m]):
            point_on(owner, "brick:Electrical_Meter", tag, _elec_point_class(tag))

    # 5. Building total energy -> a utility meter under the electrical system.
    tot = "entity:QNL_TotalEnergy"
    declare_owner(tot, "para:Utility_Meter", ELEC, ELEC_CLASS)
    point_on(tot, "para:Utility_Meter", "QNL_TotalEnergy.Energy",
             "brick:Electrical_Energy_Usage_Sensor")

    # 6. Generator breaker ACB3, a part of the existing generator.
    gen = "entity:QNL_ELEC_Gen"
    acb3 = gen + "_ACB3"
    out.append(row(gen, "para:Generator", "brick:hasPart", acb3,
                   "brick:Circuit_Breaker",
                   [("o", "rdfs:label_en", label(acb3.replace("entity:", "")))]))
    for tag, pcls in GEN_ACB3.items():
        point_on(acb3, "brick:Circuit_Breaker", tag, pcls)

    # 7. Loose orphan points - the entity is the point, isPartOf HVAC.
    for tag, pcls in POINT_ORPHANS.items():
        if tag not in historian:
            continue
        pid = "entity:" + tag.rsplit(".", 1)[0]   # drop the .suffix
        unit = to_unit(historian[tag].get("unit", ""))
        out.append(row(pid, pcls, "brick:isPartOf", HVAC, HVAC_CLASS,
                       [("s", "rdfs:label_en", label(pid.replace("entity:", ""))),
                        ("s", "brick:hasUnit", unit)]))
        out.append(row(pid, pcls, "ref:hasExternalReference", "<blanknode>",
                       "ref:TimeseriesReference",
                       [("o", "ref:hasTimeseriesId", tag),
                        ("o", "para:hasEntityId", tag)]))
        note_para(pcls)

    for cls in list(para_used):
        para_used[cls] = PARA_DECL.get(cls, (para_used[cls] or "brick:Point",))[0] \
            or "brick:Point"
    return len(out) - n0, para_used

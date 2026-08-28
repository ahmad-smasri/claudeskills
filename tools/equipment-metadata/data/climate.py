# Climate Control Units - Museum Climate Controls MCG-10P and its ancillaries
# Source: climate_control_units_manual.pdf
CLIMATE = {}

CLIMATE["MCG-10P"] = dict(
  src="climate_control_units_manual.pdf", page=2,
  manufacturer="Museum Climate Controls", model="MCG-10P",
  equipment_type="Positive-pressure humidity control unit for display cases / storage spaces",
  doc_status="Sheet watermarked 'Preliminary'; footer 'Museum Climate Controls 2012'",
  specifications=dict(
    capacity="Up to 2,500 l/hr with single pump; 5,000 l/hr with optional VCB1000 blower",
    tolerance="+/- 2% at RH set point",
    operating_temp_c="17 to 27 (63 to 81 F)",
    power="110 VAC 50-60 Hz / 6 A",
    power_consumption="6 A at 50%RH / 21 C (average)",
    air_hose_connection="Smooth inside-surface hose, ID 25 mm",
    size="500 mm (w) x 650 mm (d) x 650 mm (h)",
    weight_kg=50, weight_lb=100, weight_note="without water",
    intake_air_filter="Activated carbon filter, supplied with the unit",
    water_feed="Reverse osmosis filter, supplied with the unit"),
  installation_requirements=[
    "Display case leakage better than 0.3 air changes per day",
    "Minimum clearance space 550 mm (W) x 700 mm (D) x 700 mm (H)",
    "Force air ventilation at least 150 CFM / ambient temperature < 23 C",
    "Water supply minimum 40 PSI",
    "Ground level floor drain or drain pan",
    "One or more 8 mm holes for air hose connections inside display case",
    "Air supply pipeline to case from unit",
    "Power outlet 220 VAC / 15 A"],
  systems_included=[
    "Reverse osmosis water filter",
    "3-way air supply diverting valve",
    "Remote RH / temperature sensor - Model MCLS-75",
    "Activated carbon and activated alumina (Al2O3) impregnated with potassium permanganate (KMnO4) intake air filter",
    "UV light clean water system"],
  features=[
    "Stackable - multiple units can stack together to condition larger volume",
    "Unit can be placed up to 100 m away",
    "Delivers humidity within 2% of set point",
    "Multilevel fault tolerant protections with display",
    "Dry contact relay connection for building management system",
    "Remote monitoring and data logging (optional)"],
  dimension_drawings=dict(pages="5-6", dwg_no="MCG10P-1 / MCG10P-2", rev="1.0",
    drawn_by="KY", date="2-10-13", scale="1:10", size="A / B",
    front_view_width_mm=475, front_view_height_mm=400, plan_view_depth_mm=430,
    side_view_width_mm=494, side_view_height_mm=425),
  source_conflict=("Specification sheet (page 2) states size 500 (w) x 650 (d) x 650 (h) mm, "
                   "while dimension drawing MCG10P-1 (page 6) shows 475 W x 430 D x 400 H mm. "
                   "Confirm with the manufacturer before using either as nameplate data."),
)

CLIMATE["VCB1000-AB32"] = dict(
  src="climate_control_units_manual.pdf", page=4,
  manufacturer="VCBtech", model="VCB1000-AB32",
  equipment_type="Optional blower/pump for MCG-10P (raises capacity to 5,000 l/hr)",
  technical_data=dict(electronics="integrated", input_voltage_v_dc=24, input_current_a=7,
    speed_rpm=9000, motor_rating_w=110, speed_control_range_rpm="700 to 9000",
    permissible_ambient_c="-10 to 40", weight_kg=1.2, spl_dba=48,
    total_pressure_difference_vacuum_mbar=100, total_pressure_difference_pressure_mbar=120,
    bearing_life_hours=20000),
  dimensions_mm=dict(flange_od=144, bolt_circle=133, body_od=114, depth=90,
    width_across=72, height=61, hub=53, mounting="8 x M4 x 6"),
  installation=dict(page=3,
    mounting="Shaft in any position; vibration within section 1 Technical Data limits",
    clearance="Minimum 15 mm each side for heat dissipation; at least 2 mm on the pump lid side"),
  control_wiring=dict(page=3,
    red="+Vcc, +24 V power supply", black="Gnd, -24 V power supply",
    green="n_des, speed reference 0-10 V DC", white="A, 10 V ground (digital input)",
    grey="B, 24 V+ (digital input)", blue="n_act",
    modes="A=0/B=0 output disabled; A=0/B=1 counter-clockwise (main direction); "
          "A=1/B=0 clockwise; A=1/B=1 breaking"),
)

CLIMATE["MCG Air Filter AF4"] = dict(
  src="climate_control_units_manual.pdf", page=7,
  manufacturer="Museum Climate Controls", model="AF4",
  equipment_type="Three-stage intake air filter for MCG units",
  designed_for="Light gases (ammonia NH3, formaldehyde CH2O, hydrogen sulfide H2S, sulfur dioxide SO2), "
               "particulates, gaseous pollutants, odors",
  stages=dict(
    primary='3/4" (20 mm) polyester media - removes particulates',
    secondary="Granular activated carbon + activated alumina (Al2O3) impregnated with "
              "potassium permanganate (KMnO4) - removes light gases and odors",
    tertiary='3/4" (20 mm) polyurethane foam media - removes stray particulates or carbon'),
  specifications=dict(gac_alumina_wts_per_sqft="150/225",
    nominal_thickness='secondary filter - 2" (50 mm)',
    initial_resistance="0.11 at 100 FPM", final_resistance="1.2 (in WG)",
    average_arrestance="90-96 % at 300 FPM",
    particulates_capacity="235 g/ft2 or 4035 g/m2",
    filter_dimension='4" x 4" x 2" (100 x 100 x 50 mm)',
    filter_case_dimension='11" x 4.50" x 4.5" (280 x 115 x 115 mm)',
    hose_connections="20 mm ID for MCG4, 32 mm ID for MCG8"),
  options="Alarm for filter expiration",
  warranty="One year parts and labor",
  features=["Booster fan for stand-alone usage or to compensate air resistance in long-distance connection",
            "Low air resistance"],
  note="Hose connection sizes are quoted for MCG4 and MCG8; the sheet does not state a size for MCG-10P.",
)

# Step 1 — do the selected datapoints exist?

| Source | Rows |
|---|---|
| Selected datapoints | 2769 |
| Historian tags | 11601 (5574 analog, 6027 discrete) |
| Register assets, 4 families | 449 |

## 0. Only column A of the selected-points file is usable

The file holds **two independent lists side by side**, not one list with seven columns. Column A/B (`TagName`, `DP Integration`) runs to 2,769 rows and is the selected list. Columns C-G (`DP Name`, `Units`, `Tag-Reference`, `Equip-Name`, `Point-Name`) stop at row 2,435, cover a different set of tags, and are sorted independently - of the 2,434 rows where both blocks have values, the `DP Name` agrees with the `Point-Name` on **15**. Row 26 reads `QNL_AHUB002_RtnAirDuctPrs.PV` against a `DP Name` of `RtnFan1_AutoManCmd`.

So the equipment/part/point split is taken from column A's tag, resolved against the asset register, and the unit of measure and description are taken from the historian. Nothing here reads columns C-G. Reconstructing tags from `Equip-Name` + `Point-Name` also produces 51 tags that are in no other source, some visibly corrupt (`QNL_CCU_B01..unSts`).

## 1. Every selected datapoint is in the historian

2769 of 2769 selected tags matched a historian tag exactly - no normalising, no case folding.

**15 tags appear twice in column A** - one per AHU, all `RtnAirDuctPrs.PV`, once in the main block and once in the 335-row addendum below it. Confirmed with you as an artefact of appending the addendum, not two distinct points: deduplicate on the tag, so each AHU gets the point once.

## 2. The join to the asset register

| Family | Register assets | With datapoints | Selected rows |
|---|---|---|---|
| AHUB | 15 | 15 | 524 |
| VAV | 246 | 245 | 779 |
| CAV | 51 | 50 | 156 |
| FCU | 137 | 137 | 771 |

**Datapoints for assets the register does not have (6 rows, 2 assets).** They are real - the historian carries them - but no ontology subject exists to hang them on:

  - `QNL_CAV_1F_S15_001` — 8 historian tags
  - `QNL_VAV_B_S13_005` — 8 historian tags

**Register assets with no selected datapoints (2).**

  - `QNL_CAV_B_S13_050` (CAV) — 0 historian tags, no telemetry at all. **Highlight its row and note that it can carry no points**
  - `QNL_VAV_1F_S15_039S` (VAV) — 8 historian tags, available but not selected. Confirmed a real distinct asset, not a typo of its sibling: **highlight its row and note that it has telemetry nobody selected**

## 3. What each family actually carries

A unit only gets the points its own tags prove it has, so these counts are the input to the triples, not a template to apply uniformly.

### AHUB — 15 units, 86 distinct points, 66 distinct part tokens

| Point | Units | Unit of measure | Historian description |
|---|---|---|---|
| `CHWRtnTemp.PV` | 15/15 | °C | Process Value |
| `CHWSupTemp.PV` | 15/15 | °C | Process Value |
| `CoolVlv.PosFbk` | 15/15 | % | QNL AHU-B0007 Cooling Valve TV-2300 |
| `EnableDisableCmd` | 15/15 | — | Enable/Disable Command (1=Enable, 0=Disable) |
| `FrshAirTemp.PV` | 15/15 | °C | Process Value |
| `MixAirTemp.PV` | 15/15 | °C | Process Value |
| `RtnAirDuctPrs.PV` | 15/15 | Pa | Process Value |
| `RtnAirHumd.PV` | 15/15 | %rH | Process Value |
| `RtnAirTemp.PV` | 15/15 | °C | Process Value |
| `RtnHumiditySP` | 15/15 | %rH | QNL AHU-B0007 Basement Level AHU Plant Room B04 |
| `SupAirDuctPrs.PV` | 15/15 | Pa | Process Value |
| `SupAirFlow.PV` | 15/15 | m/s | Process Value |
| `SupAirHumd.PV` | 15/15 | %rH | Process Value |
| `SupAirTemp.PV` | 15/15 | °C | Process Value |
| `SupFan.AutoManCmd` | 14/15 | — | Auto/Manual Command |
| `SupFan.FTSP` | 14/15 | — | Fail to Stop Alarm |
| `SupFan.FTST` | 14/15 | — | Fail to Start Alarm |
| `SupFan.SpeedFbk` | 14/15 | % | Speed Feedback |
| `SupFan.TripAlm` | 14/15 | — | Trip Alarm |
| `SupFan.kW` | 14/15 | % | Power |
| `SupFan.kWH` | 14/15 | kWh | Energy |
| `AvgSpcHumd.PV` | 9/15 | %rH | Process Value |
| `AvgSpcTemp.PV` | 9/15 | °C | Process Value |
| `IntrnlEADmpr.PositionCtrl` | 7/15 | % | QNL AHU-B0012 Internal Exhaust Air Damper MD-2651F |
| `IntrnlFADmpr.PositionCtrl` | 7/15 | % | QNL AHU-B0012 Internal Fresh Air Damper MD-2651B |
| … 61 more | | | |

### VAV — 246 units, 4 distinct points, 1 distinct part tokens

| Point | Units | Unit of measure | Historian description |
|---|---|---|---|
| `DmprPos` | 245/246 | % | Damper Position |
| `DuctAirFlow` | 245/246 | l/s | Duct Air Flow |
| `EffectiveSP` | 245/246 | °C | Effective Temperature Setpoint |
| `RmTemp` | 44/246 | °C | Room/Space Temperature |

### CAV — 51 units, 4 distinct points, 1 distinct part tokens

| Point | Units | Unit of measure | Historian description |
|---|---|---|---|
| `DmprPos` | 50/51 | % | Damper Position |
| `DuctAirFlow` | 50/51 | l/s | Duct Air Flow |
| `EffectiveSP` | 50/51 | °C | Effective Temperature Setpoint |
| `RmTemp` | 6/51 | °C | Room/Space Temperature |

### FCU — 137 units, 7 distinct points, 1 distinct part tokens

| Point | Units | Unit of measure | Historian description |
|---|---|---|---|
| `CalcEntryScheduledHrs` | 137/137 | hrs | ScheduledPM Hours (Manual Entry) |
| `CalcEntryUnscheduledHrs` | 137/137 | hrs | UnScheduled Outage Hours (Manual Entry) |
| `EffectiveSP` | 137/137 | °C | QNL 1F-Z3 P2 Bridge Ceiling Void BR5 FCU-0041 |
| `ValveFbk` | 137/137 | % | QNL 1F-Z3 P2 Bridge Ceiling Void BR5 FCU-0041 |
| `RtnAirTemp` | 82/137 | °C | Return Air Temperature |
| `RtnTempSP` | 82/137 | °C | Return Air Temperature SetPoint |
| `RmTemp` | 59/137 | °C | QNL BF-Z2 P2 S1 Security Stores FCU-0010 |


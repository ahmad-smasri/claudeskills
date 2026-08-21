# Step 2 — the decision ledger

2221 selected rows in scope collapse to **101 distinct signatures**.

| Outcome | Signatures | Meaning |
|---|---|---|
| `auto` | 24 | the ladder answered: Dar Cairo at 0.60+, or a real Brick 1.4 term |
| `needs-you: confirm` | 73 | a plausible Dar Cairo candidate, below the bar |
| `needs-you` | 4 | no match, or the only Brick term is deprecated/an alias |

Of the 24 resolved automatically, 21 came from Dar Cairo and 3 from Brick 1.4.

Parts: 28 signatures hang a point under a part, 73 put the point directly on the equipment.

## Same point, different answer across families — settle these first

| Part | Point | Families disagree on |
|---|---|---|
| — | `RmTemp` | para:Room_Air_Temperature (needs-you); para:Room_Air_Temperature (auto) |

## AHUB — 86 signatures

| Part | Point | Units | Proposed class | Score | Dar Cairo uses | Status |
|---|---|---|---|---|---|---|
| — | `EnableDisableCmd` | 15/15 | *brick:On_Off_Command?* | 0.14 | 68 | needs-you: no match - propose a para: class |
| — | `RtnHumiditySP` | 15/15 | brick:Return_Air_Humidity_Setpoint | 0.29 | 52 | auto |
| `CHWRtnTemp` | `PV` | 15/15 | brick:Chilled_Water_Return_Temperature_Sensor | 0.80 | 5 | auto |
| `CHWSupTemp` | `PV` | 15/15 | brick:Chilled_Water_Supply_Temperature_Sensor | 0.80 | 4 | auto |
| `CoolVlv` | `PosFbk` | 15/15 | *brick:Valve_Position_Sensor?* | 0.40 | 24 | needs-you: confirm the Dar Cairo candidate |
| `FrshAirTemp` | `PV` | 15/15 | brick:Outside_Air_Temperature_Sensor | 0.75 | 3 | auto |
| `MixAirTemp` | `PV` | 15/15 | brick:Mixed_Air_Temperature_Sensor | 0.50 | 1 | auto |
| `RtnAirDuctPrs` | `PV` | 15/15 | *brick:Return_Air_Temperature_Sensor?* | 0.33 | 24 | needs-you: confirm the Dar Cairo candidate |
| `RtnAirHumd` | `PV` | 15/15 | brick:Return_Air_Humidity_Sensor | 0.75 | 20 | auto |
| `RtnAirTemp` | `PV` | 15/15 | brick:Return_Air_Temperature_Sensor | 0.75 | 24 | auto |
| `SupAirDuctPrs` | `PV` | 15/15 | *brick:Supply_Air_Static_Pressure_Sensor?* | 0.50 | 52 | needs-you: confirm the Dar Cairo candidate |
| `SupAirFlow` | `PV` | 15/15 | brick:Supply_Air_Flow_Sensor | 0.75 | 18 | auto |
| `SupAirHumd` | `PV` | 15/15 | brick:Supply_Air_Humidity_Sensor | 0.75 | 3 | auto |
| `SupAirTemp` | `PV` | 15/15 | brick:Supply_Air_Temperature_Sensor | 0.75 | 20 | auto |
| `SupFan` | `AutoManCmd` | 14/15 | *brick:On_Off_Command?* | 0.33 | 68 | needs-you: confirm the Dar Cairo candidate |
| `SupFan` | `FTSP` | 14/15 | *brick:Alarm?* | 0.25 | 33 | needs-you: confirm the Dar Cairo candidate |
| `SupFan` | `FTST` | 14/15 | *brick:Alarm?* | 0.25 | 33 | needs-you: confirm the Dar Cairo candidate |
| `SupFan` | `SpeedFbk` | 14/15 | *para:Over_Speed_Sensor?* | 0.25 | 1 | needs-you: confirm the Dar Cairo candidate |
| `SupFan` | `TripAlm` | 14/15 | *brick:Alarm?* | 0.50 | 33 | needs-you: confirm the Dar Cairo candidate |
| `SupFan` | `kW` | 14/15 | brick:Electric_Power_Sensor | 0.67 | 713 | auto |
| `SupFan` | `kWH` | 14/15 | *brick:Electrical_Energy_Usage_Sensor?* | 0.50 | 819 | needs-you: confirm the Dar Cairo candidate |
| `AvgSpcHumd` | `PV` | 9/15 | *brick:Relative_Humidity_Sensor?* | 0.20 | 110 | needs-you: no match - propose a para: class |
| `AvgSpcTemp` | `PV` | 9/15 | *brick:Temperature_Sensor?* | 0.25 | 110 | needs-you: confirm the Dar Cairo candidate |
| `IntrnlEADmpr` | `PositionCtrl` | 7/15 | brick:Damper_Position_Command | 0.67 | 29 | auto |
| `IntrnlFADmpr` | `PositionCtrl` | 7/15 | brick:Damper_Position_Command | 0.67 | 29 | auto |
| `RtnAirFlow` | `PV` | 7/15 | brick:Return_Air_Flow_Sensor | 0.75 | 15 | auto |
| `IntrnlEADmpr` | `PositionFbk` | 6/15 | *brick:Damper_Position_Sensor?* | 0.29 | 74 | needs-you: confirm the Dar Cairo candidate |
| `IntrnlFADmpr` | `PositionFbk` | 6/15 | *brick:Damper_Position_Sensor?* | 0.29 | 74 | needs-you: confirm the Dar Cairo candidate |
| `RtnFan` | `AutoManCmd` | 6/15 | *brick:On_Off_Command?* | 0.33 | 68 | needs-you: confirm the Dar Cairo candidate |
| `RtnFan` | `SpeedFbk` | 6/15 | *para:Over_Speed_Sensor?* | 0.25 | 1 | needs-you: confirm the Dar Cairo candidate |
| `RtnFan` | `TripAlm` | 6/15 | *brick:Alarm?* | 0.50 | 33 | needs-you: confirm the Dar Cairo candidate |
| `RtnFan` | `kW` | 6/15 | brick:Electric_Power_Sensor | 0.67 | 713 | auto |
| `RtnFan` | `kWH` | 6/15 | *brick:Electrical_Energy_Usage_Sensor?* | 0.50 | 819 | needs-you: confirm the Dar Cairo candidate |
| `SpcHumd01` | `PV` | 6/15 | *brick:Relative_Humidity_Sensor?* | 0.25 | 110 | needs-you: confirm the Dar Cairo candidate |
| `SpcHumd02` | `PV` | 6/15 | *brick:Relative_Humidity_Sensor?* | 0.25 | 110 | needs-you: confirm the Dar Cairo candidate |
| `SpcHumd03` | `PV` | 6/15 | *brick:Relative_Humidity_Sensor?* | 0.25 | 110 | needs-you: confirm the Dar Cairo candidate |
| `SpcHumd04` | `PV` | 6/15 | *brick:Relative_Humidity_Sensor?* | 0.25 | 110 | needs-you: confirm the Dar Cairo candidate |
| `SpcHumd05` | `PV` | 5/15 | *brick:Relative_Humidity_Sensor?* | 0.25 | 110 | needs-you: confirm the Dar Cairo candidate |
| `SpcTemp01` | `PV` | 5/15 | *brick:Temperature_Sensor?* | 0.33 | 110 | needs-you: confirm the Dar Cairo candidate |
| `SpcTemp02` | `PV` | 5/15 | *brick:Temperature_Sensor?* | 0.33 | 110 | needs-you: confirm the Dar Cairo candidate |
| … 46 more, see ledger.csv | | | | | | |

## VAV — 4 signatures

| Part | Point | Units | Proposed class | Score | Dar Cairo uses | Status |
|---|---|---|---|---|---|---|
| — | `DmprPos` | 245/246 | brick:Damper_Position_Sensor | 0.67 | 74 | auto |
| — | `DuctAirFlow` | 245/246 | *brick:Air_Flow_Sensor?* | 0.50 | 23 | needs-you: confirm the Dar Cairo candidate |
| — | `EffectiveSP` | 245/246 | *brick:Cooling_Temperature_Setpoint?* | 0.50 | 52 | needs-you: confirm the Dar Cairo candidate |
| — | `RmTemp` | 44/246 | *para:Room_Air_Temperature?* | 0.50 | 52 | needs-you: confirm the Dar Cairo candidate |

## CAV — 4 signatures

| Part | Point | Units | Proposed class | Score | Dar Cairo uses | Status |
|---|---|---|---|---|---|---|
| — | `DmprPos` | 50/51 | brick:Damper_Position_Sensor | 0.67 | 74 | auto |
| — | `DuctAirFlow` | 50/51 | *brick:Air_Flow_Sensor?* | 0.50 | 23 | needs-you: confirm the Dar Cairo candidate |
| — | `EffectiveSP` | 50/51 | *brick:Cooling_Temperature_Setpoint?* | 0.50 | 52 | needs-you: confirm the Dar Cairo candidate |
| — | `RmTemp` | 6/51 | *para:Room_Air_Temperature?* | 0.50 | 52 | needs-you: confirm the Dar Cairo candidate |

## FCU — 7 signatures

| Part | Point | Units | Proposed class | Score | Dar Cairo uses | Status |
|---|---|---|---|---|---|---|
| — | `CalcEntryScheduledHrs` | 137/137 | *para:Operation_Hours?* | 0.20 | 200 | needs-you: no match - propose a para: class |
| — | `CalcEntryUnscheduledHrs` | 137/137 | *para:Operation_Hours?* | 0.17 | 200 | needs-you: no match - propose a para: class |
| — | `EffectiveSP` | 137/137 | *brick:Cooling_Temperature_Setpoint?* | 0.50 | 52 | needs-you: confirm the Dar Cairo candidate |
| — | `ValveFbk` | 137/137 | *brick:Valve_Position_Sensor?* | 0.50 | 24 | needs-you: confirm the Dar Cairo candidate |
| — | `RtnAirTemp` | 82/137 | brick:Return_Air_Temperature_Sensor | 0.75 | 24 | auto |
| — | `RtnTempSP` | 82/137 | brick:Return_Air_Temperature_Setpoint | 0.50 | 20 | auto |
| — | `RmTemp` | 59/137 | para:Room_Air_Temperature | 0.67 | 52 | auto |


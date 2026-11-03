# Field-level data dictionary

All IDs are required, immutable strings and unique within their entity. Foreign keys are required except optional `CheckInEvent` (a no-show has no check-in). Booleans are lowercase `true`/`false`; timestamps are ISO-8601; dates are `YYYY-MM-DD`; time fields are local `HH:MM`. Capacity/count/pallet values are positive integers; service and early/late values are minutes.

| Table | Field | Type | Requirement, allowed values, uniqueness and validation |
|---|---|---|---|
| Facility | facility_id | string | Required; unique PK; `FAC-###`. |
|  | name, city, timezone | string | Required; nonempty; timezone is an IANA zone. |
|  | effective_from | date | Required; valid ISO date; starts facility applicability. |
|  | status | enum | Required; `active`, `inactive`. |
| Dock | dock_id | string | Required; unique PK; `DOCK-<facility_id>-###`. |
|  | facility_id | string | Required FK to Facility. |
|  | dock_type | enum | Required; `standard`, `reefer`, `hazmat`, `mixed`. |
|  | hazmat_certified, reefer_power, active | boolean | Required; lowercase boolean. Dock capability must satisfy handling requirements. |
| YardSlot | yard_slot_id | string | Required unique PK; `YARD-<facility_id>-###`. |
|  | facility_id | string | Required FK to Facility. |
|  | slot_type | enum | Required; `standard`, `reefer`. |
|  | capacity | integer | Required; > 0. |
|  | active | boolean | Required. |
| Carrier | carrier_id | string | Required unique PK; `CAR-###-##`. |
|  | name | string | Required; nonempty. |
|  | active | boolean | Required. |
| Vehicle | vehicle_id | string | Required unique PK; `VEH-###-##`. |
|  | carrier_id | string | Required FK to Carrier. |
|  | vehicle_type | string | Required; generated `tractor_trailer`. |
|  | capacity_pallets | integer | Required; > 0; shipment pallets cannot exceed capacity. |
|  | reefer_capable, hazmat_certified, active | boolean | Required. |
| Shipment | shipment_id | string | Required unique PK; `SHP-2026-######`. |
|  | facility_id, carrier_id, vehicle_id | string | Required FKs to Facility, Carrier and Vehicle. |
|  | direction | enum | Required; `inbound` or `outbound`. |
|  | pallets | integer | Required; > 0 and no greater than referenced vehicle capacity. |
|  | temperature_controlled, hazardous | boolean | Required; flags determine handling needs. |
|  | handling_requirement_id | string | Required unique FK to HandlingRequirement; 1:1. |
|  | requested_date | date | Required; within the simulation horizon. |
| HandlingRequirement | handling_requirement_id | string | Required unique PK; `REQ-######`. |
|  | shipment_id | string | Required unique FK to Shipment; 1:1. |
|  | required_dock_type | enum | Required; `standard`, `reefer`, or `hazmat`. |
|  | min_service_minutes, max_service_minutes | integer | Required; minutes; min > 0 and max >= min. |
|  | requires_reefer, requires_hazmat | boolean | Required; capabilities must be present at assigned dock/vehicle. |
| LaborShift | labor_shift_id | string | Required unique PK; `SHIFT-<facility-id>-YYYYMMDD`. |
|  | facility_id | string | Required FK to Facility. |
|  | shift_date | date | Required; valid date in 60-day generated calendar. |
|  | start_time, end_time | time | Required; `HH:MM`; end after start. |
|  | team_count | integer | Required; > 0. |
|  | active | boolean | Required. |
| Appointment | appointment_id | string | Required unique PK; `APPT-2026-######`. |
|  | shipment_id | string | Required unique FK to Shipment; one appointment per generated shipment. |
|  | facility_id, carrier_id, vehicle_id | string | Required FKs. Must agree with shipment parent IDs. |
|  | dock_id, yard_slot_id | string | Required FKs to Dock and YardSlot at the same facility. |
|  | appointment_date | date | Required; scheduled operating date. |
|  | window_start, window_end | time | Required; `HH:MM`; end after start. |
|  | service_minutes | integer | Required; minutes; within requirement duration bounds. |
|  | status | enum | Required; `scheduled`, `rejected_capacity`, or `no_show`. |
|  | scheduled_at | timestamp | Required; request decision timestamp. |
| CheckInEvent | checkin_id | string | Required unique PK; `CHECK-<appointment-id>-##`. |
|  | appointment_id | string | Required FK to Appointment. |
|  | event_time | timestamp | Required; may precede appointment date only in labeled anomaly. |
|  | event_type | enum | Required; generated `check_in`. |
|  | minutes_early_late | integer | Required; minutes relative to scheduled window start. |
| Exception | exception_id | string | Required unique PK; `EXC-######`. |
|  | appointment_id | string | Required FK to Appointment. |
|  | issue_type | enum | Required; the five documented anomaly labels. |
|  | cause_code | enum | Required; `DOCK_CAPACITY`, `DOCK_COMPATIBILITY`, `EARLY_DATE`, `LABOR_UNAVAILABLE`, `NO_SHOW`. |
|  | severity | enum | Required; `low`, `medium`, or `high`. |
|  | detected_at | timestamp | Required; explicit detection time. |
|  | resolution_status | enum | Required; `open`, `resolved`, `waived`. |
| Event | event_id | string | Required unique PK; `EVT-######-##`. |
|  | appointment_id | string | Required FK to Appointment. |
|  | event_type | enum | Required; `request_created`, `appointment_decision`, `check_in`, `handling_completed`, `departed`, `no_show_detected`, `exception_raised`, `appointment_closed`. |
|  | event_time | timestamp | Required; lifecycle order except where an anomaly deliberately violates a rule. |
|  | source | string | Required; generated `simulator`. |
|  | details | string | Optional descriptive text. |
| GroundTruth | label_id | string | Required unique PK; `GT-######`. |
|  | appointment_id | string | Required FK to Appointment; one known label per injected issue. |
|  | issue_type | enum | Required; one of the five documented edge cases. |
|  | expected_decision | enum | Required; generated `reject_or_flag`. |
|  | rule | string | Required; matching cause code used to derive label. |

## Cardinality and lifecycle

Facility 1:N Dock, YardSlot, LaborShift, Shipment and Appointment. Carrier 1:N Vehicle, Shipment and Appointment. Vehicle 1:N Shipment and Appointment over time. Shipment 1:1 HandlingRequirement and 1:1 Appointment in this generated workload. Dock and YardSlot each have 1:N historical Appointment assignments; each Appointment has one selected Dock and YardSlot. Appointment 1:N Event; Appointment 0:1 CheckInEvent; Appointment 0:1 Exception in this generated anomaly set. GroundTruth labels are held in their own table and do not belong to operational input feature tables. The dataset uses no many-to-many relationship requiring a bridge table.

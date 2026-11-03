# Project requirements supplied by the requester

This document preserves the requester’s project instructions in professional language. It excludes assistant-generated explanations, setup replies, and unrelated conversation.

## Core objective

Build an end-to-end logistics scheduling solution that creates inbound and outbound appointments against dock, yard, labor, vehicle, and time-window constraints. The solution must expose key decisions and exceptions, preserve traceability, and produce measurable outputs.

## Required workflow

1. Generate or reference master data first: facilities, docks, yard slots, carriers, and vehicles.
2. Generate dependent transaction and event records using valid parent IDs.
3. Create dock and yard capacity calendars.
4. Define shipment handling requirements and service durations.
5. Generate carrier appointment requests and allocate compatible slots.
6. Simulate check-in, unloading/loading, departure, no-shows, early arrivals, and congestion.
7. Persist state changes as explicit records or events; do not overwrite history.
8. Generate outcomes and ground-truth labels from documented rules rather than independent random assignment.

## Required entities and data rules

The solution must define primary keys for Facility, Dock, YardSlot, Carrier, Vehicle, Appointment, Shipment, LaborShift, HandlingRequirement, CheckInEvent, and Exception. Every relationship must use a foreign key, and the documentation must state cardinality, optionality, effective dates, and lifecycle states. Many-to-many relationships require bridge tables. Deliberate anomalies must retain an `issue_type` or ground-truth label.

Identifiers must be deterministic, immutable, zero-padded, and consistent across files. Examples include `FAC-001`, `DOCK-<facility-id>-001`, `APPT-2026-000001`, `SHP-2026-000001`, and `CHECK-<appointment-id>-01`.

## Synthetic data requirements

The baseline workload must be parameterized and generated with a fixed seed, such as `20261022`, so starter and full datasets use the same logic. The target scale is:

- 10 facilities
- 100 docks
- 20,000 appointments
- 100,000 events
- 60-day operating horizon

The workload must include refrigerated loads, hazardous handling, peak congestion, and realistic variation.

## Required labeled negative scenarios

The valid baseline must be generated first. Then inject and label these edge cases:

- Overlapping appointments that exceed dock capacity.
- Incompatible load assigned to a dock or vehicle.
- Check-in before the appointment date.
- Labor shift not available.
- No-show not recorded.

The known labels must be exported separately as CSV or JSON and must not leak into operational input features.

## Validation requirements

The project must validate primary-key uniqueness, foreign-key integrity, allowed enums, date ordering, arithmetic reconciliation, lifecycle transitions, duplicate records, capacity rules, compatibility rules, utilization, wait time, exception cause codes, and event timeline validity.

It must export CSV, JSON, and SQL seed data where applicable, together with a README, schema/data dictionary, generator command, fixed seed, source manifest, and validation summary. It must regenerate twice with the same seed and compare row counts or checksums to demonstrate reproducibility.

## Provenance requirements

External data is optional. If used, the project must record the source URL, dataset version, retrieval date, license or terms, attribution, transformations, and discarded fields. Data must be legally permitted for access and redistribution. Synthetic data is preferred when suitability or licensing is unclear, and no confidential or personal information should be collected.

## Submission expectations

The finished project must be runnable locally, documented in a public repository, and accompanied by any requested tests. The final reviewer should be able to understand the scheduling rules, entities, exception labels, validation evidence, reproducibility, API, and dashboard without additional assistance.

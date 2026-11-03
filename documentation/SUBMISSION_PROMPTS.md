# SmartDock submission prompts

Use these polished prompts when presenting the project, explaining it to a reviewer, or asking another developer to extend it.

## Project summary prompt

> SmartDock is a deterministic logistics appointment scheduling and operations control tower. It schedules inbound and outbound shipments against dock, yard, vehicle, labor, compatibility, and time-window constraints. The project generates synthetic master and transaction data, preserves lifecycle event history, labels five deliberate exception scenarios, exposes operational metrics through a FastAPI service, and presents the results in a responsive browser dashboard.

## Technical implementation prompt

> Build and maintain SmartDock as a reproducible full-stack logistics scheduling demo. Generate valid parent data first for facilities, docks, yard slots, carriers, vehicles, labor shifts, shipments, and handling requirements. Allocate appointments only when dock capability, vehicle capability, yard capacity, service duration, and labor availability are compatible. Emit immutable request, decision, check-in, handling, departure, no-show, exception, and closure events. Use fixed seed `20261022`, deterministic IDs, CSV/JSON/SQLite exports, primary and foreign-key validation, and a separate `ground_truth.csv` for known anomaly labels. Serve the data through a FastAPI API and render a responsive operations control tower with summary metrics, searchable appointment queue, pagination, and exception review.

## Reviewer demo prompt

> Demonstrate SmartDock from the operator’s point of view. Start the API, open the control tower, review total appointments, scheduled capacity, average wait, and open exceptions. Search the appointment queue by facility or dock, filter by lifecycle status, inspect the exception register, then open `/docs` to show the documented API endpoints. Explain that all records are synthetic, the seed is fixed, and the validation summary proves row counts, joins, event timelines, compatibility checks, and separate ground-truth labels.

## Product design prompt

> Design a calm, professional logistics control tower for planners and operations managers. Use a dark navy navigation rail, a light neutral workspace, teal success signals, amber exception signals, compact KPI cards, a high-signal appointment table, clear status badges, responsive layouts, accessible labels, and plain operational language. The interface should prioritize decisions and exceptions over decorative elements.

## Extension prompt

> Extend SmartDock without changing the deterministic data contract. Add a planner workflow that can propose an alternative compatible dock and time window for a rejected appointment, record the decision as a new immutable event, preserve the previous state, and expose the recommendation through a new API endpoint. Add validation for the recommendation, update the dashboard with a review action, and document the rule and output fields.

## Submission description

> SmartDock solves dock appointment coordination for a multi-facility logistics network. The solution combines a fixed-seed synthetic data generator, rule-based scheduling, explicit lifecycle events, exception ground truth, a constrained SQLite export, a FastAPI service, and an operations dashboard. It demonstrates capacity allocation, refrigerated and hazardous compatibility, labor availability, no-shows, early arrivals, congestion, traceability, measurable wait and utilization metrics, validation, and reproducibility.

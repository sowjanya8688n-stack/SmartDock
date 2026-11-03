# SmartDock implementation notes

## Scheduling and capacity

The generator creates valid parent records before dependent records. For each shipment request it searches 30-minute candidate starts, verifies dock equipment, vehicle capability, yard-slot availability and daily labor allowance, then reserves every dock and yard interval covered by its service duration. It assigns `rejected_capacity` when it cannot find a valid slot. Service minutes are selected before allocation and used to calculate reserved time and lifecycle timestamps.

Demand is seeded and weighted toward selected peak dates. The baseline still preserves valid assignments; known failures are added afterward and labeled. Five labeled cases cover dock overlap, incompatible dock, pre-date check-in, unavailable labor shift and missing check-in for a no-show. `ground_truth.csv` remains a separate evaluation output.

## Metrics shown in the dashboard

- **Average wait**: for valid same-date check-ins, minutes from gate arrival until the appointment window when early, plus the simulated 10-minute gate handoff. The deliberately invalid pre-date check-in is excluded.
- **Dock utilization**: scheduled service minutes divided by available dock minutes over the 60-day calendar.
- **Schedule counts**: accepted, capacity-rejected and no-show appointments, derived from appointment rows.

## API and data storage

The API reads the generated CSVs as its operational source so all endpoints reproduce the same seeded data. `appointments.sqlite` is the relational export with primary, unique and foreign-key constraints. The older `backend/models` files are retained as the initial SQLAlchemy schema draft; the current dashboard API does not mutate the generated dataset.

## Data and validation outputs

Run `python scripts/generate_data.py` to regenerate all files under `backend/generated_data`. `manifest.json` provides table sizes and CSV checksums; `validation_summary.json` reports uniqueness, foreign-key, relationship consistency, allocation compatibility, date ordering, event count/timeline and ground-truth checks.

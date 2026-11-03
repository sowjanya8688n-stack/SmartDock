# SmartDock

SmartDock is a deterministic dock and yard appointment scheduling control tower for inbound and outbound logistics. It generates a realistic synthetic workload, allocates compatible dock and yard capacity, simulates appointment lifecycle events, labels known failures, and serves the results through a FastAPI API and browser dashboard.

The implementation covers the challenge workflow: master data first, dependent transactions second, rule-based allocation, labor and equipment constraints, explicit event history, exception ground truth, measurable outcomes, reproducibility, and validation.

## What is included

- Python generator with fixed seed `20261022`.
- 10 facilities, 100 docks, 200 yard slots, 50 carriers, 500 vehicles, and 600 labor shifts.
- 20,000 appointments, 20,000 shipments, and 100,000 lifecycle events over 60 days.
- Refrigerated and hazardous handling requirements with dock and vehicle capability checks.
- Dock and yard reservations in 30-minute intervals with service-duration and labor limits.
- Five labeled edge cases: overlapping appointments, incompatible load assignment, pre-date check-in, unavailable labor, and an unrecorded no-show.
- CSV exports, a constrained SQLite export, a manifest of checksums, and a validation summary.
- FastAPI endpoints and a dark operations control tower dashboard with appointments, dock schedule, yard/labor status, shipment mix, analytics, exception center, generator history, and settings views.

All operational records are synthetic. No external or personal data is used.

## Requirements

- Windows PowerShell, macOS Terminal, or Linux shell.
- Python 3.10 or newer.
- A modern browser. Google Chrome is recommended for the dashboard.
- Node.js and npm are not required for the current frontend: it is served as HTML, CSS, and JavaScript by FastAPI. The repository can be migrated to React later without changing the API contract.

## Fresh setup

Clone the repository and enter it:

```powershell
git clone <YOUR_PUBLIC_REPOSITORY_URL>
cd SmartDock
```

Create and activate the Python environment on Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Install the exact backend dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

The current `backend/requirements.txt` contains FastAPI, Uvicorn, and SQLAlchemy. The generator itself uses Python’s standard library and does not need pandas, NumPy, Faker, or a separate database server.

## Generate the dataset

Generate the full challenge workload:

```powershell
python scripts\generate_data.py
```

Generate a smaller starter workload while keeping the same rules and seed:

```powershell
python scripts\generate_data.py --appointments 500 --seed 20261022 --out backend\generated_data
```

The generator writes to `backend/generated_data` by default. It creates:

`facilities.csv`, `docks.csv`, `yard_slots.csv`, `carriers.csv`, `vehicles.csv`, `shipments.csv`, `handling_requirements.csv`, `labor_shifts.csv`, `appointments.csv`, `checkin_events.csv`, `exceptions.csv`, `events.csv`, `ground_truth.csv`, `appointments.sqlite`, `manifest.json`, and `validation_summary.json`.

`ground_truth.csv` is a separate evaluation output. Do not use it as an operational model feature.

The generator validates primary-key uniqueness, foreign-key joins, appointment relationships, vehicle capacity, dock and vehicle compatibility, date ordering, event lifecycle count and order, and expected ground-truth labels. A successful run writes `"valid": true` in `validation_summary.json`.

## Run the application

From the repository root, with the virtual environment active:

```powershell
python -m uvicorn backend.main:app --reload
```

Open the dashboard:

```text
http://127.0.0.1:8000/
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

To open Chrome from PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\open_chrome.ps1
```

Keep the Uvicorn terminal open while using the dashboard. Press `Ctrl+F5` in Chrome after frontend changes so cached CSS and JavaScript do not hide the latest version.

## API reference

- `GET /api/health` — service and generated-data readiness.
- `GET /api/summary` — appointments, schedule outcomes, exceptions, events, wait time, and dock utilization.
- `GET /api/facilities` — facility master records.
- `GET /api/docks?facility_id=FAC-001` — dock records, optionally filtered by facility.
- `GET /api/labor-shifts?facility_id=FAC-001` — labor shifts, optionally filtered by facility.
- `GET /api/carriers` — carrier master records.
- `GET /api/vehicles?carrier_id=CAR-001-01` — vehicle records, optionally filtered by carrier.
- `GET /api/shipments?limit=100` — shipment records.
- `GET /api/appointments?q=&status=&limit=&offset=` — searchable, filtered appointment page.
- `GET /api/exceptions` — labeled operational exceptions.
- `GET /api/ground-truth` — separate evaluation labels.
- `GET /api/data-status` — generation manifest and checksums.

## Project structure

```text
SmartDock/
├── backend/
│   ├── main.py                 FastAPI app and CSV-backed API
│   ├── requirements.txt        Runtime dependencies
│   ├── database.py             SQLAlchemy base from the initial schema draft
│   ├── models/                 Relational schema reference
│   └── generated_data/         Reproducible CSV, JSON, and SQLite outputs
├── frontend/
│   ├── index.html               Dashboard markup and category views
│   ├── styles.css               Main dark control-tower theme
│   ├── category-extra.css       Exception, analytics, and history styles
│   └── app.js                   API calls, navigation, filters, and charts
├── scripts/
│   ├── generate_data.py         Deterministic generator and validation
│   └── open_chrome.ps1          Opens the local dashboard in Chrome
├── documentation/
│   ├── DATA_DICTIONARY.md       Field-level definitions and relationships
│   ├── DASHBOARD_CATEGORIES.md  Dashboard information architecture
│   ├── PROJECT_NOTES.md         Scheduling, metrics, and storage notes
│   ├── SUBMISSION_PROMPTS.md    Presentation and extension prompts
│   └── AI_REQUIREMENTS.md       User-provided project requirements, rewritten
└── .vscode/launch.json          VS Code API debug configuration
```

## Data model and scheduling rules

The generator creates parent records before children and uses immutable deterministic IDs such as `FAC-001`, `DOCK-FAC-001-001`, `APPT-2026-000001`, `SHP-2026-000001`, and `CHECK-APPT-2026-000001-01`.

An appointment can be scheduled only when the selected dock and yard interval are available, the vehicle has enough pallet capacity, refrigerated and hazardous requirements are compatible, and the facility’s labor allowance has not been exhausted. Rejected requests retain their source relationships and receive the `rejected_capacity` status. Lifecycle records are appended as events; history is not overwritten.

## Reproducibility check

Run the same command into two different directories and compare the `sha256` values in their `manifest.json` files:

```powershell
python scripts\generate_data.py --appointments 500 --seed 20261022 --out .\repro-a
python scripts\generate_data.py --appointments 500 --seed 20261022 --out .\repro-b
```

The CSV checksums should match. The generator’s CSV output is the reproducibility reference; SQLite file bytes can vary by SQLite runtime.

## Development workflow

1. Make generator or API changes.
2. Run `python scripts\generate_data.py` and inspect `validation_summary.json`.
3. Run `python -m uvicorn backend.main:app --reload`.
4. Open the dashboard and test the category navigation, appointment search, status filter, pagination, and exception center.
5. Run `node --check frontend\app.js` after JavaScript changes.
6. Update the relevant documentation when fields, routes, rules, or output files change.

## Known architecture boundary

The current API reads generated CSVs as its operational source. `appointments.sqlite` is the validated relational export. The SQLAlchemy files under `backend/models` are retained as a schema reference from the original scaffold; they are not used by the current read-only dashboard API. A future persistence phase can connect those models to the API without changing the external CSV contract.

## Further improvements

- Add automated API tests for every endpoint and filter combination.
- Add a CI workflow that runs generation, validation, Python checks, and JavaScript syntax checks.
- Add a database migration tool if the SQLAlchemy schema becomes the primary persistence layer.
- Add real aggregate endpoints for yard utilization, labor availability, shipment mix, and generation history.
- Add planner actions that propose and record alternative slots as immutable events.

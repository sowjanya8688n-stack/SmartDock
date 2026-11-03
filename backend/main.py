from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "backend" / "generated_data"
WEB = ROOT / "frontend"
app = FastAPI(title="SmartDock | Dock Appointment Operations", version="1.0.0", description="Synthetic dock, yard and labor appointment scheduling demonstration")


def rows(name: str) -> list[dict]:
    file = DATA / f"{name}.csv"
    if not file.exists():
        return []
    with file.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def row_count(name: str) -> int:
    file = DATA / f"{name}.csv"
    if not file.exists():
        return 0
    with file.open(encoding="utf-8-sig") as f:
        return max(0, sum(1 for _ in f) - 1)


@app.get("/api/health")
def health():
    return {"status": "ok", "data_ready": (DATA / "appointments.csv").exists()}


@app.get("/api/summary")
def summary():
    appts = rows("appointments")
    checks = rows("checkin_events")
    exceptions = rows("exceptions")
    facilities = rows("facilities")
    docks = rows("docks")
    wait = []
    by_id = {a["appointment_id"]: a for a in appts}
    for check in checks:
        if check.get("event_type") != "check_in":
            continue
        appt = by_id.get(check["appointment_id"])
        if appt:
            try:
                arrival = datetime.fromisoformat(check["event_time"])
                slot_start = datetime.fromisoformat(appt["appointment_date"] + "T" + appt["window_start"])
                if arrival.date() != slot_start.date():
                    continue
                # Gate arrival waits until the slot when early, then 10 minutes for the modeled dock handoff.
                wait.append(max(0, (slot_start - arrival).total_seconds() / 60) + 10)
            except ValueError:
                pass
    scheduled = sum(a.get("status") == "scheduled" for a in appts)
    return {"facilities": len(facilities), "docks": len(docks), "appointments": len(appts), "scheduled": scheduled,
            "rejected": sum(a.get("status") == "rejected_capacity" for a in appts),
            "no_shows": sum(a.get("status") == "no_show" for a in appts),
            "exceptions": len(exceptions), "events": row_count("events"),
            "average_wait_minutes": round(sum(wait) / len(wait), 1) if wait else 0,
            "dock_utilization_pct": round(sum(int(a["service_minutes"]) for a in appts if a.get("status") == "scheduled") / max(1, len(docks) * 60 * 16 * 60) * 100, 1)}


@app.get("/api/facilities")
def facilities():
    return rows("facilities")


@app.get("/api/docks")
def docks(facility_id: str = ""):
    data = rows("docks")
    return [d for d in data if not facility_id or d.get("facility_id") == facility_id]


@app.get("/api/labor-shifts")
def labor_shifts(facility_id: str = ""):
    data = rows("labor_shifts")
    return [s for s in data if not facility_id or s.get("facility_id") == facility_id]


@app.get("/api/carriers")
def carriers():
    return rows("carriers")


@app.get("/api/vehicles")
def vehicles(carrier_id: str = ""):
    data = rows("vehicles")
    return [v for v in data if not carrier_id or v.get("carrier_id") == carrier_id]


@app.get("/api/shipments")
def shipments(limit: int = Query(default=100, ge=1, le=1000)):
    return rows("shipments")[:limit]


@app.get("/api/appointments")
def appointments(q: str = "", status: str = "", limit: int = Query(default=100, ge=1, le=1000), offset: int = Query(default=0, ge=0)):
    data = rows("appointments")
    if status:
        data = [a for a in data if a.get("status", "").lower() == status.lower()]
    if q:
        key = q.lower()
        data = [a for a in data if any(key in str(a.get(field, "")).lower() for field in ("appointment_id", "shipment_id", "facility_id", "carrier_id", "dock_id"))]
    return {"total": len(data), "items": data[offset:offset + limit]}


@app.get("/api/exceptions")
def exceptions():
    return rows("exceptions")


@app.get("/api/ground-truth")
def ground_truth():
    return rows("ground_truth")


@app.get("/api/data-status")
def data_status():
    manifest = DATA / "manifest.json"
    if not manifest.exists():
        return {"ready": False, "message": "Generate data with python scripts/generate_data.py"}
    import json
    return {"ready": True, "manifest": json.loads(manifest.read_text(encoding="utf-8-sig"))}


@app.get("/", include_in_schema=False)
def dashboard():
    page = WEB / "index.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="Dashboard files are missing")
    return FileResponse(page)

app.mount("/static", StaticFiles(directory=str(WEB), check_dir=False), name="static")


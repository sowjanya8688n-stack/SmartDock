# SmartDock dashboard categories

The landing page follows an operations manager’s decision flow.

| Category | Information shown | Why it matters |
|---|---|---|
| Dashboard | Total appointments, scheduled volume, exceptions, wait time and daily capacity | Gives the manager a quick network health signal. |
| Appointments | Appointment ID, shipment, facility, dock, time window, service duration and lifecycle status | Lets planners find a booking and understand its current decision. |
| Dock & Yard | Dock schedule by hour, dock assignment, yard utilization and facility selector | Prevents overlapping use and makes physical capacity visible. |
| Shipments | Dry, refrigerated, hazardous and other load mix | Shows the handling profile that drives compatibility rules. |
| Labor Shifts | Labor availability and shift coverage | Connects appointment decisions to staffing constraints. |
| Carriers & Vehicles | Carrier and vehicle relationships, capacity and equipment capability | Supports vehicle compatibility and traceable ownership. |
| Exceptions | Overlap, handling mismatch, early check-in, labor unavailable and no-show cases | Gives planners actionable causes with ground-truth labels. |
| Analytics | Wait time, utilization, rejected capacity and trend measures | Provides measurable evaluation outputs. |
| Data Generator | Seed, scale, manifests, row counts and validation results | Makes the synthetic dataset reproducible and reviewable. |
| Settings | Future home for facility, service-window and rule configuration | Keeps operational rules separate from the dashboard view. |

The frontend uses real generated appointment and exception records. The illustrative yard, labor and shipment-mix indicators are presented as an operator summary and can be connected to dedicated API endpoints when those aggregate tables are added.

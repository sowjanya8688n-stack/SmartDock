
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class ExceptionRecord(Base):
    __tablename__ = "exceptions"

    __table_args__ = (
        CheckConstraint(
            "exception_type IN ('DOCK_UNAVAILABLE', 'YARD_CAPACITY', 'LABOR_SHORTAGE', 'VEHICLE_INCOMPATIBLE', 'HANDLING_MISMATCH', 'LATE_ARRIVAL', 'NO_SHOW', 'TIME_WINDOW_CONFLICT', 'OTHER')",
            name="check_exception_type"
        ),
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="check_exception_severity"
        ),
        CheckConstraint(
            "status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'CLOSED')",
            name="check_exception_status"
        ),
    )

    exception_id = Column(String(40), primary_key=True)

    appointment_id = Column(
        String(30),
        ForeignKey("appointments.appointment_id"),
        nullable=True
    )

    facility_id = Column(
        String(20),
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    exception_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(String(20), default="OPEN", nullable=False)

    description = Column(Text, nullable=False)

    detected_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    resolution_notes = Column(Text, nullable=True)

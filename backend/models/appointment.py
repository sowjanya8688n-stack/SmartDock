
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func

from database import Base


class Appointment(Base):

    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "appointment_status IN ('REQUESTED', 'SCHEDULED', 'CHECKED_IN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW')",
            name="check_appointment_status"
        ),
        CheckConstraint(
            "scheduled_end > scheduled_start",
            name="check_appointment_time"
        ),
        CheckConstraint(
            "service_duration_minutes > 0",
            name="check_service_duration"
        ),
    )

    appointment_id = Column(
        String(30),
        primary_key=True
    )

    shipment_id = Column(
        String(30),
        ForeignKey("shipments.shipment_id"),
        nullable=False
    )

    facility_id = Column(
        String(20),
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    dock_id = Column(
        String(30),
        ForeignKey("docks.dock_id"),
        nullable=True
    )

    vehicle_id = Column(
        String(30),
        ForeignKey("vehicles.vehicle_id"),
        nullable=False
    )

    scheduled_start = Column(
        DateTime,
        nullable=False
    )

    scheduled_end = Column(
        DateTime,
        nullable=False
    )

    service_duration_minutes = Column(
        Integer,
        nullable=False
    )

    appointment_status = Column(
        String(30),
        default="REQUESTED",
        nullable=False
    )

    priority = Column(
        Integer,
        default=3,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )


from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func
from database import Base


class AppointmentYardSlot(Base):
    __tablename__ = "appointment_yard_slots"

    __table_args__ = (
        CheckConstraint(
            "assigned_to > assigned_from",
            name="check_yard_assignment_time"
        ),
        CheckConstraint(
            "status IN ('ASSIGNED', 'OCCUPIED', 'RELEASED', 'CANCELLED')",
            name="check_yard_assignment_status"
        ),
    )

    appointment_id = Column(
        String(30),
        ForeignKey("appointments.appointment_id"),
        primary_key=True
    )

    yard_slot_id = Column(
        String(30),
        ForeignKey("yard_slots.yard_slot_id"),
        primary_key=True
    )

    assigned_from = Column(DateTime, nullable=False)
    assigned_to = Column(DateTime, nullable=False)

    status = Column(String(20), default="ASSIGNED", nullable=False)

    created_at = Column(DateTime, server_default=func.now())

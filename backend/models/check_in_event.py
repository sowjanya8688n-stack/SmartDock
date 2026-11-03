
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint
)
from sqlalchemy.sql import func

from database import Base


class CheckInEvent(Base):

    __tablename__ = "check_in_events"

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('ARRIVED', 'CHECKED_IN', 'CHECKED_OUT', 'DEPARTED', 'NO_SHOW')",
            name="check_event_type"
        ),
    )

    check_in_event_id = Column(
        String(40),
        primary_key=True
    )

    appointment_id = Column(
        String(30),
        ForeignKey("appointments.appointment_id"),
        nullable=False
    )

    event_type = Column(
        String(30),
        nullable=False
    )

    event_time = Column(
        DateTime,
        nullable=False
    )

    recorded_by = Column(
        String(100),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

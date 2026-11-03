
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func

from database import Base


class LaborShift(Base):

    __tablename__ = "labor_shifts"

    __table_args__ = (
        CheckConstraint(
            "total_workers >= 0",
            name="check_total_workers"
        ),
        CheckConstraint(
            "available_workers >= 0",
            name="check_available_workers"
        ),
        CheckConstraint(
            "available_workers <= total_workers",
            name="check_worker_availability"
        ),
        CheckConstraint(
            "shift_end > shift_start",
            name="check_shift_time"
        ),
    )

    labor_shift_id = Column(
        String(30),
        primary_key=True
    )

    facility_id = Column(
        String(20),
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    shift_name = Column(
        String(50),
        nullable=False
    )

    shift_start = Column(
        DateTime,
        nullable=False
    )

    shift_end = Column(
        DateTime,
        nullable=False
    )

    total_workers = Column(
        Integer,
        nullable=False
    )

    available_workers = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )


from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func

from database import Base


class YardSlot(Base):

    __tablename__ = "yard_slots"

    __table_args__ = (
        CheckConstraint(
            "slot_status IN ('AVAILABLE', 'OCCUPIED', 'MAINTENANCE')",
            name="check_yard_slot_status"
        ),
        CheckConstraint(
            "capacity >= 1",
            name="check_yard_slot_capacity"
        ),
    )

    yard_slot_id = Column(String(30), primary_key=True)

    facility_id = Column(
        String(20),
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    slot_name = Column(String(100), nullable=False)

    slot_status = Column(
        String(20),
        default="AVAILABLE",
        nullable=False
    )

    capacity = Column(Integer, default=1, nullable=False)

    is_active = Column(Boolean, default=True)

    effective_from = Column(DateTime, nullable=False)

    effective_to = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

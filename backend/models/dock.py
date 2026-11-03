
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func

from database import Base


class Dock(Base):

    __tablename__ = "docks"

    __table_args__ = (
        CheckConstraint(
            "dock_type IN ('INBOUND', 'OUTBOUND', 'BOTH')",
            name="check_dock_type"
        ),
    )

    dock_id = Column(String(30), primary_key=True)

    facility_id = Column(
        String(20),
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    dock_name = Column(String(100), nullable=False)

    dock_type = Column(String(20), nullable=False)

    max_vehicle_length_m = Column(Float, nullable=False)

    max_weight_kg = Column(Float, nullable=False)

    is_active = Column(Boolean, default=True)

    effective_from = Column(DateTime, nullable=False)

    effective_to = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

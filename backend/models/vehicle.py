
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func

from database import Base


class Vehicle(Base):

    __tablename__ = "vehicles"

    __table_args__ = (
        CheckConstraint(
            "vehicle_status IN ('AVAILABLE', 'IN_USE', 'MAINTENANCE', 'INACTIVE')",
            name="check_vehicle_status"
        ),
        CheckConstraint(
            "max_weight_kg > 0",
            name="check_vehicle_weight"
        ),
        CheckConstraint(
            "vehicle_length_m > 0",
            name="check_vehicle_length"
        ),
    )

    vehicle_id = Column(
        String(30),
        primary_key=True
    )

    carrier_id = Column(
        String(30),
        ForeignKey("carriers.carrier_id"),
        nullable=False
    )

    vehicle_number = Column(
        String(30),
        unique=True,
        nullable=False
    )

    vehicle_type = Column(
        String(50),
        nullable=False
    )

    max_weight_kg = Column(
        Float,
        nullable=False
    )

    vehicle_length_m = Column(
        Float,
        nullable=False
    )

    vehicle_status = Column(
        String(20),
        default="AVAILABLE",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    effective_from = Column(
        DateTime,
        nullable=False
    )

    effective_to = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

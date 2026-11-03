
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func

from database import Base


class Shipment(Base):

    __tablename__ = "shipments"

    __table_args__ = (
        CheckConstraint(
            "shipment_direction IN ('INBOUND', 'OUTBOUND')",
            name="check_shipment_direction"
        ),
        CheckConstraint(
            "shipment_status IN ('PLANNED', 'READY', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED')",
            name="check_shipment_status"
        ),
        CheckConstraint(
            "weight_kg > 0",
            name="check_shipment_weight"
        ),
        CheckConstraint(
            "quantity >= 1",
            name="check_shipment_quantity"
        ),
    )

    shipment_id = Column(
        String(30),
        primary_key=True
    )

    shipment_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    facility_id = Column(
        String(20),
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    carrier_id = Column(
        String(30),
        ForeignKey("carriers.carrier_id"),
        nullable=False
    )

    shipment_direction = Column(
        String(20),
        nullable=False
    )

    origin = Column(
        String(150),
        nullable=False
    )

    destination = Column(
        String(150),
        nullable=False
    )

    weight_kg = Column(
        Float,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    shipment_status = Column(
        String(30),
        default="PLANNED",
        nullable=False
    )

    expected_arrival = Column(
        DateTime,
        nullable=True
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

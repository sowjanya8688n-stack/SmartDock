
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class ShipmentHandlingRequirement(Base):
    __tablename__ = "shipment_handling_requirements"

    shipment_id = Column(
        String(30),
        ForeignKey("shipments.shipment_id"),
        primary_key=True
    )

    requirement_id = Column(
        String(30),
        ForeignKey("handling_requirements.requirement_id"),
        primary_key=True
    )

    created_at = Column(DateTime, server_default=func.now())

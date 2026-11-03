
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    UniqueConstraint
)
from sqlalchemy.sql import func

from database import Base


class Carrier(Base):

    __tablename__ = "carriers"

    __table_args__ = (
        UniqueConstraint(
            "carrier_code",
            name="unique_carrier_code"
        ),
    )

    carrier_id = Column(
        String(30),
        primary_key=True
    )

    carrier_name = Column(
        String(100),
        nullable=False
    )

    carrier_code = Column(
        String(30),
        nullable=False
    )

    contact_person = Column(
        String(100),
        nullable=True
    )

    email = Column(
        String(100),
        nullable=True
    )

    phone = Column(
        String(20),
        nullable=True
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


from sqlalchemy import (
    Column,
    String,
    Boolean,
    Text,
    DateTime,
    UniqueConstraint
)
from sqlalchemy.sql import func

from database import Base


class HandlingRequirement(Base):

    __tablename__ = "handling_requirements"

    __table_args__ = (
        UniqueConstraint(
            "requirement_code",
            name="unique_requirement_code"
        ),
    )

    requirement_id = Column(
        String(30),
        primary_key=True
    )

    requirement_code = Column(
        String(50),
        nullable=False
    )

    requirement_name = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    requires_refrigeration = Column(
        Boolean,
        default=False,
        nullable=False
    )

    requires_special_equipment = Column(
        Boolean,
        default=False,
        nullable=False
    )

    requires_safety_procedure = Column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
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

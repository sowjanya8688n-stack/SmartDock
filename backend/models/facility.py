
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func

from database import Base


class Facility(Base):

    __tablename__ = "facilities"

    facility_id = Column(String(20), primary_key=True)

    facility_name = Column(String(100), nullable=False)

    address = Column(String(200), nullable=False)

    city = Column(String(50), nullable=False)

    state = Column(String(50), nullable=False)

    country = Column(String(50), nullable=False)

    timezone = Column(String(50), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())

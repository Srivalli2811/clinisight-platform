from sqlalchemy import Column, Integer, String, Date, Enum, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=True)
    gender = Column(Enum("Male", "Female", "Other"), nullable=True)
    phone = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    registered_at = Column(TIMESTAMP, server_default=func.now())
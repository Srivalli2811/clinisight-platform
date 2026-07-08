from sqlalchemy import Column, Integer, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=True)
    appointment_date = Column(DateTime, nullable=True)
    status = Column(Enum("Scheduled", "Completed", "Cancelled"), nullable=True)
    notes = Column(Text, nullable=True)
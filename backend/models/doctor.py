from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    doctor_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=True)
    dept_id = Column(Integer, ForeignKey("departments.dept_id"), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(15), nullable=True)
    department = relationship("Department", back_populates="doctors")
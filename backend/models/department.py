from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"
    dept_id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=True)
    doctors = relationship("Doctor", back_populates="department")
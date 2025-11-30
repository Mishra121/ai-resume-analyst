from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from db.base import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    file_path = Column(String, nullable=False)
    text_md = Column(String, nullable=False)  # full extracted markdown

    employee = relationship("Employee", backref="resumes")

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from db.base import Base

class ResumeChunk(Base):
    __tablename__ = "resume_chunks"

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # text-embedding-3-small dim size

    resume = relationship("Resume", backref="chunks")

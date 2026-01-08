from app.database import Base
from sqlalchemy import Column,Integer,String,TIMESTAMP,Text,ForeignKey,text,Enum
from sqlalchemy.orm import relationship

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    # 🔑 THIS IS THE FIX
    submissions = relationship(
        "Submission",
        secondary="submission_tags",
        back_populates="tags"
    )
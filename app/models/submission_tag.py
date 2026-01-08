from app.database import Base
from sqlalchemy import Column,Integer,String,TIMESTAMP,Text,ForeignKey,text,Enum
from sqlalchemy.orm import relationship

class SubmissionTag(Base):
    __tablename__ = "submission_tags"
    submission_id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
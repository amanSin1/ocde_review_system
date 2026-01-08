from app.database import Base
from sqlalchemy import Column,Integer,String,TIMESTAMP,Text,ForeignKey,text,Enum
from sqlalchemy.orm import relationship

class Annotation(Base):
    __tablename__ = "annotations"
    id = Column(Integer, primary_key = True, index = True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable = False)
    line_number = Column(Integer, nullable = False)
    comment_text = Column(Text, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable= False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable= False, server_default=text('now()'), onupdate=text('now()'))
    review = relationship("Review", back_populates="annotations")

from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class SubmissionCreate(BaseModel):
    title : str
    description : str
    code_content : str
    language : str
    tags : Optional[List[str]] = []

    
class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    code_content: Optional[str] = None

class SubmissionResponse(BaseModel):
    id: int
    title: str
    status:str
    updated_at: datetime
    class Config:
        from_attributes = True

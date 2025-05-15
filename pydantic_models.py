from pydantic import BaseModel,Field
from enum import Enum
from datetime import datetime

class ModelName(str , Enum):
    GEMINI = "gemini-2.0-flash"
    GEMINI_PRO = "gemini-2.0-flash-lite"
    
class QueryInput(BaseModel):
    question: str
    session_id: str = Field(None, title="Session ID", description="Session ID for the user")
    model:ModelName = Field(default=ModelName.GEMINI)
    
class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model:ModelName
    
class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime
    
class DeleteFileRequest(BaseModel):
    file_id: int
    

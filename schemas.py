from pydantic import BaseModel, Field
from typing import List, Optional


class ProcessFileRequest(BaseModel):
    file_path: str = Field(..., description="Path to the file to be processed")
    options: Optional[List[str]] = Field(None, description="List of processing options")    
    
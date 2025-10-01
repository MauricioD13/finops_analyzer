from pydantic import BaseModel, Field
from typing import List, Optional


class ProcessFileRequest(BaseModel):
    provider: Optional[str] = Field(None, description="The cloud provider (e.g., AWS, GCP, Azure)")
    provider_detection: str = Field(..., description="Method for provider detection (e.g., auto, manual)")
    file_content: bytes = Field(..., description="Content of the uploaded file")
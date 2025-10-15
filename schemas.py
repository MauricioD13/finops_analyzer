from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ProcessFileRequest(BaseModel):
    provider: Optional[Literal["aws","azure","oracle","gcp", None]] = Field(None, description="The cloud provider (e.g., AWS, GCP, Azure)")
    provider_detection: Literal["manual","automatic"] = Field(..., description="Method for provider detection (e.g., auto, manual)")
    file_content: bytes = Field(..., description="Content of the uploaded file")
    file_path: str = Field(max_length=2000, description="Temp file path")
    file_name: str = Field(max_length=2000, description="File name")
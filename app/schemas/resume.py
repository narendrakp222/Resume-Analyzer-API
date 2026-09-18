from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    message: str = "Resume uploaded successfully"

    model_config = ConfigDict(from_attributes=True)


class ResumeResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    ats_score: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


from typing import List, Optional
from pydantic import BaseModel, Field


class JobMatchRequest(BaseModel):
    job_description: str = Field(..., min_length=20, json_schema_extra={"example": "We are looking for a Python Backend Developer with FastAPI, PostgreSQL, Docker, and AWS experience..."})
    resume_id: Optional[int] = Field(None, description="Optional resume ID. If not provided, your latest uploaded resume will be analyzed.")



class JobMatchResponse(BaseModel):
    resume_id: int
    match_percentage: float
    matching_skills: List[str]
    missing_keywords: List[str]
    suggested_improvements: List[str]
    summary: str

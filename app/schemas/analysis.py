from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict


class AnalysisResultResponse(BaseModel):
    id: int
    resume_id: int
    ats_score: Optional[int] = None
    extracted_skills: List[str]
    missing_skills: List[str]
    keyword_count: Dict[str, int]
    suggestions: List[str]
    summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeScoreResponse(BaseModel):
    ats_score: int
    skills_found: List[str]
    missing_skills: List[str]
    suggestions: List[str]

    model_config = ConfigDict(from_attributes=True)


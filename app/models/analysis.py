from datetime import datetime
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.resume import Resume


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    extracted_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    missing_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    keyword_count: Mapped[Dict[str, int]] = mapped_column(JSON, default=dict)
    suggestions: Mapped[List[str]] = mapped_column(JSON, default=list)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship("Resume", back_populates="analysis_result")

    def __repr__(self) -> str:
        return f"<AnalysisResult id={self.id} resume_id={self.resume_id}>"

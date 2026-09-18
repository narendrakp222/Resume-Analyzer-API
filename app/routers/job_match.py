from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.job_match import JobMatchRequest, JobMatchResponse
from app.services.pdf_service import PDFService
from app.services.job_matcher_service import JobMatcherService

router = APIRouter(tags=["Job Match"])


@router.post(
    "/job-match",
    response_model=JobMatchResponse,
    summary="Match resume against job description"
)
async def match_job_description(
    payload: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare resume content against a targeted software engineering job description.
    Returns match percentage, matching skills, missing keywords, and custom recommendations.
    """
    if payload.resume_id:
        result = await db.execute(
            select(Resume).where(Resume.id == payload.resume_id, Resume.user_id == current_user.id)
        )
        resume = result.scalar_one_or_none()
    else:
        # Get user's latest uploaded resume
        result = await db.execute(
            select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.upload_date.desc())
        )
        resume = result.scalars().first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )

    # Extract PDF text
    extracted_text = PDFService.extract_text_from_file(resume.file_path)
    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text could not be extracted."
        )

    match_result = JobMatcherService.match_resume_to_job(
        resume_text=extracted_text,
        job_description=payload.job_description
    )

    return JobMatchResponse(
        resume_id=resume.id,
        match_percentage=match_result["match_percentage"],
        matching_skills=match_result["matching_skills"],
        missing_keywords=match_result["missing_keywords"],
        suggested_improvements=match_result["suggested_improvements"],
        summary=match_result["summary"]
    )

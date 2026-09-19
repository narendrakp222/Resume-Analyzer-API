from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import AnalysisResult
from app.schemas.analysis import AnalysisResultResponse, ResumeScoreResponse
from app.services.pdf_service import PDFService
from app.services.analyzer_service import ResumeAnalyzerService

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze/{resume_id}",
    response_model=AnalysisResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze uploaded resume PDF"
)
async def analyze_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract text, detect skills, calculate ATS score out of 100, find missing skills, and generate actionable feedback.
    """
    # Verify resume exists and belongs to current user
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )

    # Extract PDF text
    extracted_text = PDFService.extract_text_from_file(resume.file_path)
    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file appears to be empty or unreadable text."
        )

    # Perform analysis
    analysis_data = ResumeAnalyzerService.analyze(extracted_text)

    # Check if analysis already exists for this resume
    analysis_result_obj = await db.execute(
        select(AnalysisResult).where(AnalysisResult.resume_id == resume_id)
    )
    existing_analysis = analysis_result_obj.scalar_one_or_none()

    if existing_analysis:
        existing_analysis.extracted_skills = analysis_data["extracted_skills"]
        existing_analysis.missing_skills = analysis_data["missing_skills"]
        existing_analysis.keyword_count = analysis_data["keyword_count"]
        existing_analysis.suggestions = analysis_data["suggestions"]
        existing_analysis.summary = analysis_data["summary"]
        analysis_record = existing_analysis
    else:
        analysis_record = AnalysisResult(
            resume_id=resume.id,
            extracted_skills=analysis_data["extracted_skills"],
            missing_skills=analysis_data["missing_skills"],
            keyword_count=analysis_data["keyword_count"],
            suggestions=analysis_data["suggestions"],
            summary=analysis_data["summary"]
        )
        db.add(analysis_record)

    # Update resume's overall ATS score
    resume.ats_score = analysis_data["ats_score"]

    await db.commit()
    await db.refresh(analysis_record)

    response = AnalysisResultResponse.model_validate(analysis_record)
    response.ats_score = resume.ats_score
    return response


@router.get(
    "/score/{resume_id}",
    response_model=ResumeScoreResponse,
    summary="Get ATS score and feedback for resume"
)
async def get_resume_score(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ATS score, skills found, missing skills, and suggestions for a resume.
    """
    # Fetch resume
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )

    # Fetch analysis result
    analysis_obj = await db.execute(
        select(AnalysisResult).where(AnalysisResult.resume_id == resume_id)
    )
    analysis = analysis_obj.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume has not been analyzed yet. Please run POST /analyze/{resume_id} first."
        )

    return ResumeScoreResponse(
        ats_score=resume.ats_score or 0,
        skills_found=analysis.extracted_skills,
        missing_skills=analysis.missing_skills,
        suggestions=analysis.suggestions
    )

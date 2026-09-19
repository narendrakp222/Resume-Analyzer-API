import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse, ResumeResponse

router = APIRouter(tags=["Resumes"])


@router.post(
    "/upload-resume",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload resume PDF file"
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a resume PDF file. Validates file extension, size, and saves metadata.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    # Read content to check size
    content = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # Ensure uploads directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate unique filename to prevent collisions
    unique_prefix = uuid.uuid4().hex[:8]
    safe_filename = f"{unique_prefix}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving file to disk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file."
        )

    # Save metadata to DB
    new_resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)

    return ResumeUploadResponse(
        id=new_resume.id,
        filename=new_resume.filename,
        upload_date=new_resume.upload_date,
        message="Resume uploaded successfully."
    )


@router.get(
    "/my-resumes",
    response_model=List[ResumeResponse],
    summary="Get user uploaded resumes"
)
async def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all resumes uploaded by the current authenticated user.
    """
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.upload_date.desc())
    )
    resumes = result.scalars().all()
    return resumes

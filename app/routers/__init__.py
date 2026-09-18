from app.routers.auth import router as auth_router
from app.routers.resumes import router as resumes_router
from app.routers.analysis import router as analysis_router
from app.routers.job_match import router as job_match_router

__all__ = ["auth_router", "resumes_router", "analysis_router", "job_match_router"]

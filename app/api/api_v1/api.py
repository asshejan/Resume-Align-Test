from fastapi import APIRouter

from app.api.api_v1.endpoints import jobs

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"]) 
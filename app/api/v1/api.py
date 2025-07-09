from fastapi import APIRouter

from app.api.v1.endpoints import jobs
from app.api.v1.endpoints import cv_modify

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(cv_modify.router, tags=["cv_modify"]) 
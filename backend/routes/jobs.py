"""Jobs/Roles reference routes"""
import logging
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from schemas import JobRecommendRequest, JobRecommendResponse, JobRecommendItem
from utils.job_loader import JobLoader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["reference"])

job_loader = JobLoader()


class JobResponse(BaseModel):
    id: int
    title: str
    level: str


@router.get("/", response_model=List[JobResponse])
async def get_all_jobs():
    """Get all available jobs with metadata"""
    roles = job_loader.get_job_roles()
    jobs = []
    for idx, role in enumerate(roles):
        jobs.append({
            "id": idx + 1,
            "title": role,
            "level": "mid"  # Default level, can be customized per job
        })
    return jobs


@router.get("/roles")
async def get_all_roles():
    """Get all available job roles"""
    return {"roles": job_loader.get_job_roles()}


@router.get("/role/{role_name}")
async def get_role_skills(role_name: str):
    """Get required skills for a specific role"""
    try:
        skills = job_loader.get_job_skills(role_name)
        return {
            "role": role_name,
            "skills": sorted(list(skills))
        }
    except ValueError as e:
        return {"error": str(e)}, 404


@router.post("/recommend", response_model=JobRecommendResponse)
async def recommend_jobs(request: JobRecommendRequest):
    """Return top 3 matching roles based on provided skills"""
    if not request.user_skills:
        raise HTTPException(status_code=400, detail="No skills provided")

    user_skills = {s.lower().strip() for s in request.user_skills if s.strip()}
    if not user_skills:
        raise HTTPException(status_code=400, detail="No valid skills provided")

    recommendations: List[JobRecommendItem] = []
    for role in job_loader.get_job_roles():
        role_skills = {s.lower() for s in job_loader.get_job_skills(role)}
        if not role_skills:
            continue
        matching = sorted(user_skills & role_skills)
        missing = sorted(role_skills - user_skills)
        score = len(matching) / len(role_skills)
        recommendations.append(
            JobRecommendItem(
                role=role,
                score=round(score, 3),
                matching_skills=matching,
                missing_skills=missing,
            )
        )

    recommendations.sort(key=lambda r: (r.score, len(r.matching_skills)), reverse=True)
    return JobRecommendResponse(recommendations=recommendations[:3])

"""Analysis routes for skill gap and feedback"""
import json
import logging
from fastapi import APIRouter, HTTPException, Request, Body
from schemas import GapAnalysisRequest, FeedbackResponse, SkillGapResponse
from services.skill_analysis import SkillAnalysisService
from utils.job_loader import JobLoader
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["analysis"])

# Initialize services
skill_service = SkillAnalysisService()
job_loader = JobLoader()
rate_limiter = RateLimiter(limit=30, window_seconds=600)  # 30 requests / 10 minutes per IP+endpoint


@router.post("/gap", response_model=SkillGapResponse)
async def analyze_skill_gap(request: GapAnalysisRequest, http_request: Request):
    """Analyze skill gap between user and job requirements"""
    try:
        client_ip = http_request.client.host if http_request.client else "unknown"
        if not rate_limiter.allow((client_ip, "/analyze/gap")):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
        # Log raw request data
        logger.info("=" * 80)
        logger.info("REQUEST RECEIVED: /analyze/gap")
        logger.info("=" * 80)
        
        # Log the request object details
        logger.info(f"Request Type: {type(request)}")
        logger.info(f"Request Object: {request}")
        logger.info(f"Request Dict: {request.dict() if hasattr(request, 'dict') else 'N/A'}")
        
        # Log individual fields
        logger.info(f"\nFIELD ANALYSIS:")
        logger.info(f"  job_role: {request.job_role} (type: {type(request.job_role).__name__})")
        logger.info(f"  user_name: {request.user_name} (type: {type(request.user_name).__name__})")
        logger.info(f"  user_skills: {request.user_skills}")
        logger.info(f"  user_skills type: {type(request.user_skills).__name__}")
        
        if request.user_skills:
            logger.info(f"  user_skills length: {len(request.user_skills)}")
            logger.info(f"  user_skills items: {[f'{skill} ({type(skill).__name__})' for skill in request.user_skills]}")
        else:
            logger.info(f"  user_skills is None or falsy")
        
        # Check boolean conditions
        logger.info(f"\nBOOLEAN CHECKS:")
        logger.info(f"  bool(request.user_skills): {bool(request.user_skills)}")
        logger.info(f"  request.user_skills is None: {request.user_skills is None}")
        logger.info(f"  request.user_skills == []: {request.user_skills == []}")
        logger.info(f"  len(request.user_skills) if user_skills: {len(request.user_skills) if request.user_skills else 'N/A'}")
        
        # Validate role
        logger.info(f"\nVALIDATING ROLE:")
        logger.info(f"  Checking if '{request.job_role}' is valid...")
        if not job_loader.is_valid_role(request.job_role):
            logger.error(f"  ✗ Invalid role: {request.job_role}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {request.job_role}"
            )
        logger.info(f"  ✓ Role is valid")
        
        # Validate skills - must have at least one skill
        logger.info(f"\nVALIDATING SKILLS:")
        if not request.user_skills or len(request.user_skills) == 0:
            logger.warning(f"  ✗ Skills validation failed!")
            logger.warning(f"    Condition 'not request.user_skills': {not request.user_skills}")
            logger.warning(f"    Condition 'len(request.user_skills) == 0': {len(request.user_skills) == 0 if request.user_skills else 'N/A'}")
            raise HTTPException(
                status_code=400,
                detail="No skills provided. Please add skills manually or upload a resume with a readable skills section."
            )
        logger.info(f"  ✓ Skills validation passed ({len(request.user_skills)} skills)")
        
        # Get job requirements
        logger.info(f"\nGETTING JOB REQUIREMENTS:")
        job_skills = list(job_loader.get_job_skills(request.job_role))
        logger.info(f"  Job Skills Count: {len(job_skills)}")
        logger.info(f"  Job Skills: {job_skills[:5]}{'...' if len(job_skills) > 5 else ''}")
        
        # Analyze gap
        logger.info(f"\nANALYZING GAP:")
        analysis = skill_service.analyze_gap(request.user_skills, job_skills)
        logger.info(f"  Matching Skills: {len(analysis['strong_skills'])}")
        logger.info(f"  Missing Skills: {len(analysis['missing_skills'])}")
        logger.info(f"  Proficiency: {analysis['proficiency']:.1f}%")
        
        # Build response - NO auto-generation of feedback/roadmap
        # Feedback and roadmap are generated on-demand via separate endpoints
        logger.info(f"\nBUILDING RESPONSE:")
        response = SkillGapResponse(
            matching_skills=analysis["strong_skills"],
            missing_skills=analysis["missing_skills"],
            current_skills_count=len(request.user_skills),
            required_skills_count=len(job_skills),
            matching_skills_count=len(analysis["strong_skills"]),
            proficiency=analysis["proficiency"],
            ai_feedback="",  # Empty - generate on-demand
            learning_roadmap=[]  # Empty - generate on-demand
        )
        logger.info(f"  ✓ Response built successfully")
        logger.info("=" * 80)
        logger.info("✓ REQUEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
        
        response = SkillGapResponse(
            matching_skills=analysis["strong_skills"],
            missing_skills=analysis["missing_skills"],
            current_skills_count=len(request.user_skills),
            required_skills_count=len(job_skills),
            matching_skills_count=len(analysis["strong_skills"]),
            proficiency=analysis["proficiency"],
            ai_feedback=feedback,
            learning_roadmap=roadmap_strings
        )
        
        logger.info(f"Response ready with {len(response.matching_skills)} matching and {len(response.missing_skills)} missing skills")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing skill gap: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", response_model=FeedbackResponse)
async def generate_feedback(request: GapAnalysisRequest, http_request: Request):
    """Generate comprehensive feedback with gap analysis, feedback, and roadmap"""
    try:
        client_ip = http_request.client.host if http_request.client else "unknown"
        if not rate_limiter.allow((client_ip, "/analyze/feedback")):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
        # Validate role
        if not job_loader.is_valid_role(request.job_role):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {request.job_role}"
            )
        
        # Validate input
        if not request.user_skills:
            raise HTTPException(status_code=400, detail="User skills cannot be empty")
        
        # Get job requirements
        job_skills = list(job_loader.get_job_skills(request.job_role))
        
        # Analyze gap
        analysis = skill_service.analyze_gap(request.user_skills, job_skills)
        gap_analysis = SkillGapResponse(**analysis)
        
        # Generate feedback
        feedback = skill_service.generate_feedback(
            request.user_name,
            request.job_role,
            analysis
        )
        
        # Generate roadmap
        roadmap = skill_service.generate_roadmap(analysis["missing_skills"])
        
        return FeedbackResponse(
            gap_analysis=gap_analysis,
            feedback=feedback,
            roadmap=roadmap
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback-only")
async def generate_feedback_only(request: GapAnalysisRequest):
    """Generate ONLY personalized feedback (on-demand button)"""
    try:
        logger.info("=" * 80)
        logger.info("FEEDBACK GENERATION (On-Demand)")
        logger.info("=" * 80)
        
        # Validate role
        if not job_loader.is_valid_role(request.job_role):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {request.job_role}"
            )
        
        # Validate skills
        if not request.user_skills or len(request.user_skills) == 0:
            raise HTTPException(
                status_code=400,
                detail="Please add skills to get personalized feedback"
            )
        
        # Get job requirements
        job_skills = list(job_loader.get_job_skills(request.job_role))
        
        # Analyze gap
        analysis = skill_service.analyze_gap(request.user_skills, job_skills)
        
        logger.info(f"Proficiency: {analysis['proficiency']:.1f}%")
        logger.info(f"Matching: {len(analysis['strong_skills'])} skills")
        logger.info(f"Missing: {len(analysis['missing_skills'])} skills")
        
        # Generate feedback
        logger.info("Generating personalized feedback...")
        feedback = skill_service.generate_feedback(
            request.user_name,
            request.job_role,
            analysis
        )
        
        logger.info("✓ Feedback generated successfully")
        logger.info("=" * 80)
        
        return {
            "feedback": feedback,
            "proficiency": analysis["proficiency"],
            "matching_skills": analysis["strong_skills"],
            "missing_skills": analysis["missing_skills"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/roadmap-only")
async def generate_roadmap_only(request: GapAnalysisRequest):
    """Generate ONLY learning roadmap (on-demand button)"""
    try:
        logger.info("=" * 80)
        logger.info("ROADMAP GENERATION (On-Demand)")
        logger.info("=" * 80)
        
        # Validate role
        if not job_loader.is_valid_role(request.job_role):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {request.job_role}"
            )
        
        # Validate skills
        if not request.user_skills or len(request.user_skills) == 0:
            raise HTTPException(
                status_code=400,
                detail="Please add skills to get a learning roadmap"
            )
        
        # Get job requirements
        job_skills = list(job_loader.get_job_skills(request.job_role))
        
        # Analyze gap
        analysis = skill_service.analyze_gap(request.user_skills, job_skills)
        
        logger.info(f"User skills: {', '.join(request.user_skills)}")
        logger.info(f"Missing skills: {', '.join(analysis['missing_skills'][:5])}")
        logger.info(f"Target role: {request.job_role}")
        
        # Generate roadmap with context
        logger.info("Generating progressive learning roadmap...")
        roadmap_steps = skill_service.generate_roadmap(
            analysis["missing_skills"],
            request.user_skills,
            request.job_role
        )
        
        logger.info(f"✓ Roadmap generated with {len(roadmap_steps)} steps")
        logger.info("=" * 80)
        
        return {
            "roadmap": roadmap_steps,
            "current_skills": request.user_skills,
            "missing_skills": analysis["missing_skills"],
            "job_role": request.job_role
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

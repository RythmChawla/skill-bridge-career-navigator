"""Profile routes for CRUD operations"""
import json
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import List
from schemas import ProfileCreate, ProfileUpdate, ProfileResponse, ErrorResponse
from services.database_service import DatabaseService
from services.auth_service import get_optional_user
from services.skill_analysis import SkillAnalysisService
from utils.job_loader import JobLoader
from utils.pdf_parser import extract_text_from_pdf, extract_skills_from_text
from utils.resume_parser import parse_resume
from datetime import datetime
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["profiles"])

# Initialize services
db_service = DatabaseService()
job_loader = JobLoader()
skill_analysis_service = SkillAnalysisService()

# File upload directory
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


def _to_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _normalize_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _normalize_education(entries):
    normalized = []
    for item in _to_list(entries):
        if not isinstance(item, dict):
            text = _normalize_text(item)
            if text:
                normalized.append({"school": text, "degree": "", "field": "", "timeline": "", "percentage_or_gpa": ""})
            continue
        normalized.append({
            "school": _normalize_text(item.get("school")),
            "degree": _normalize_text(item.get("degree")),
            "field": _normalize_text(item.get("field")),
            "timeline": _normalize_text(item.get("timeline")),
            "percentage_or_gpa": _normalize_text(item.get("percentage_or_gpa")),
        })
    return [item for item in normalized if any(item.values())]


def _normalize_experience(entries):
    normalized = []
    for item in _to_list(entries):
        if not isinstance(item, dict):
            text = _normalize_text(item)
            if text:
                normalized.append({"job_title": text, "company": "", "duration": "", "description": ""})
            continue
        normalized.append({
            "job_title": _normalize_text(item.get("job_title")),
            "company": _normalize_text(item.get("company")),
            "duration": _normalize_text(item.get("duration")),
            "description": _normalize_text(item.get("description")),
        })
    return [item for item in normalized if any(item.values())]


def _normalize_projects(entries):
    normalized = []
    for item in _to_list(entries):
        if not isinstance(item, dict):
            text = _normalize_text(item)
            if text:
                normalized.append({"project_name": text, "description": "", "technologies": [], "duration": ""})
            continue
        tech = item.get("technologies")
        if isinstance(tech, str):
            tech = [part.strip() for part in tech.split(",") if part.strip()]
        elif tech is None:
            tech = []
        normalized.append({
            "project_name": _normalize_text(item.get("project_name")),
            "description": _normalize_text(item.get("description")),
            "technologies": tech if isinstance(tech, list) else _to_list(tech),
            "duration": _normalize_text(item.get("duration")),
        })
    return [item for item in normalized if item["project_name"] or item["description"] or item["technologies"] or item["duration"]]


@router.post("/", response_model=ProfileResponse)
async def create_profile(
    name: str = Form(...),
    target_role: str = Form(...),
    resume: UploadFile = File(None),
    skills: str = Form(None),
    current_user = Depends(get_optional_user)
):
    """Create a new user profile with optional resume upload or manual skills input"""
    try:
        # Validate role
        if not job_loader.is_valid_role(target_role):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {target_role}. Valid roles are: {', '.join(job_loader.get_job_roles())}"
            )
        
        extracted_skills = []
        parsed_meta = {}
        
        logger.info(f"Creating profile for {name} with target role: {target_role}")
        logger.info(f"Resume provided: {resume is not None}, Skills provided: {bool(skills)}")
        
        # Process resume if provided
        resume_path = None
        resume_text = None

        if resume:
            if not resume.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files are supported")
            
            logger.info(f"Processing resume file: {resume.filename}")
            
            try:
                # Create absolute path
                file_path = os.path.abspath(os.path.join(UPLOAD_DIRECTORY, resume.filename))
                logger.info(f"Full file path: {file_path}")
                
                # Save file temporarily
                logger.info(f"Creating uploads directory if needed...")
                os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
                
                logger.info(f"Writing PDF file to disk...")
                file_content = await resume.read()
                logger.info(f"File size: {len(file_content)} bytes")
                
                with open(file_path, "wb") as f:
                    bytes_written = f.write(file_content)
                logger.info(f"Wrote {bytes_written} bytes to {file_path}")
                
                # Verify file exists
                if not os.path.exists(file_path):
                    raise ValueError(f"File was not saved successfully to {file_path}")
                
                logger.info(f"File exists: {os.path.exists(file_path)}, Size: {os.path.getsize(file_path)} bytes")
                
                # Extract text from PDF
                logger.info(f"Extracting text from PDF...")
                pdf_text = extract_text_from_pdf(file_path)
                logger.info(f"PDF text extracted successfully: {len(pdf_text)} characters")
                if len(pdf_text) > 200:
                    logger.info(f"Text preview: {pdf_text[:200]}...")
                
                # 🤖 Use Gemini to extract complete structured resume information
                logger.info(f"Using Gemini to extract complete resume information...")
                extracted_resume_data = skill_analysis_service.extract_resume_info(pdf_text)
                
                # Extract skills from Gemini response
                extracted_skills = extracted_resume_data.get("skills", [])
                
                # Also try regex extraction as fallback supplement
                if not extracted_skills:
                    logger.info(f"No skills from Gemini, using regex fallback...")
                    extracted_skills = extract_skills_from_text(pdf_text)
                
                logger.info(f"✓ Skills extracted from resume: {len(extracted_skills)} skills found")
                logger.info(f"  Skills: {extracted_skills}")
                
                # Prepare parsed metadata with structured data
                parsed_meta = {
                    "email": extracted_resume_data.get("contact", {}).get("email"),
                    "phone": extracted_resume_data.get("contact", {}).get("phone"),
                    "name": extracted_resume_data.get("personal_info", {}).get("name"),
                    "location": extracted_resume_data.get("personal_info", {}).get("location"),
                    "socials": {
                        k: v for k, v in {
                            "linkedin": extracted_resume_data.get("contact", {}).get("linkedin"),
                            "github": extracted_resume_data.get("contact", {}).get("github"),
                            "portfolio": extracted_resume_data.get("contact", {}).get("portfolio")
                        }.items() if v
                    },
                    "education": _normalize_education(extracted_resume_data.get("education", [])),
                    "experience": _normalize_experience(extracted_resume_data.get("experience", [])),
                    "projects": _normalize_projects(extracted_resume_data.get("projects", []))
                }
                
                logger.info(f"✓ Gemini extracted structured data:")
                logger.info(f"  - Education: {len(parsed_meta.get('education', []))} entries")
                logger.info(f"  - Experience: {len(parsed_meta.get('experience', []))} entries")
                logger.info(f"  - Projects: {len(parsed_meta.get('projects', []))} entries")
                
                resume_path = os.path.basename(file_path)
                resume_text = pdf_text
                    
            except ValueError as e:
                logger.error(f"ValueError during PDF processing: {e}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Unexpected error during PDF processing: {e}", exc_info=True)
                raise HTTPException(status_code=400, detail=f"Error processing resume: {str(e)}")
        
        # Use manual skills if provided
        if skills:
            manual_skills = [s.strip() for s in skills.split(',') if s.strip()]
            logger.info(f"Manual skills provided: {manual_skills}")
            extracted_skills = list(set(extracted_skills + manual_skills))
            logger.info(f"Combined skills: {extracted_skills}")
        
        # Validate that at least some skills are provided
        if not extracted_skills:
            logger.warning(f"No skills found for profile {name}")
            raise HTTPException(
                status_code=400,
                detail="No skills found. Please upload a resume with clear skills section or add skills manually (comma-separated)."
            )
        
        logger.info(f"Creating profile with {len(extracted_skills)} skills: {extracted_skills}")
        
        # Create profile
        profile = db_service.create_profile(
            name=name,
            target_role=target_role,
            skills=extracted_skills,
            email=parsed_meta.get("email"),
            phone=parsed_meta.get("phone"),
            location=parsed_meta.get("location"),
            socials=parsed_meta.get("socials"),
            experience=parsed_meta.get("experience"),
            projects=parsed_meta.get("projects"),
            education=parsed_meta.get("education"),
            user_id=getattr(current_user, "id", None),
            resume_path=resume_path,
            resume_text=resume_text,
            resume_last_updated=datetime.utcnow(),
        )
        
        logger.info(f"Profile created successfully: {profile.id}")
        return ProfileResponse.from_orm(profile)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str):
    """Get a user profile by ID"""
    profile = db_service.get_profile(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    
    return ProfileResponse.from_orm(profile)


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: str, update_data: ProfileUpdate):
    """Update a user profile"""
    profile = db_service.get_profile(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    
    # Validate role if being updated
    if update_data.target_role and not job_loader.is_valid_role(update_data.target_role):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {update_data.target_role}"
        )
    
    update_dict = update_data.dict(exclude_unset=True)
    updated_profile = db_service.update_profile(profile_id, **update_dict)
    
    return ProfileResponse.from_orm(updated_profile)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def patch_profile(profile_id: str, update_data: dict):
    """Partial update of a profile"""
    profile = db_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    if "target_role" in update_data and not job_loader.is_valid_role(update_data["target_role"]):
        raise HTTPException(status_code=400, detail=f"Invalid role: {update_data['target_role']}")

    if "education" in update_data:
        update_data["education"] = _normalize_education(update_data["education"])
    if "experience" in update_data:
        update_data["experience"] = _normalize_experience(update_data["experience"])
    if "projects" in update_data:
        update_data["projects"] = _normalize_projects(update_data["projects"])

    updated = db_service.update_profile(profile_id, **update_data)
    return ProfileResponse.from_orm(updated)


@router.delete("/{profile_id}")
async def delete_profile(profile_id: str):
    """Delete a user profile"""
    success = db_service.delete_profile(profile_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    
    return {"message": f"Profile {profile_id} deleted successfully"}


@router.post("/{profile_id}/resume", response_model=ProfileResponse)
async def replace_resume(profile_id: str, resume: UploadFile = File(...)):
    """Replace resume only (no full form) - deletes old file and extracts info"""
    profile = db_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    if not resume.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Delete old resume file if it exists
    if profile.resume_path:
        old_file_path = os.path.abspath(os.path.join(UPLOAD_DIRECTORY, profile.resume_path))
        try:
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
                logger.info(f"Deleted old resume: {old_file_path}")
        except Exception as e:
            logger.warning(f"Could not delete old resume: {e}")

    resume_path = None
    resume_text = None
    parsed_meta = {}

    try:
        # Save new resume with user-specific name to avoid conflicts
        safe_filename = f"{profile_id}_resume.pdf"
        file_path = os.path.abspath(os.path.join(UPLOAD_DIRECTORY, safe_filename))
        
        logger.info(f"Processing new resume for profile {profile_id}")
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        
        file_content = await resume.read()
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Resume saved to: {file_path}")
        
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(file_path)
        logger.info(f"Extracted text: {len(pdf_text)} characters")
        
        # Use Groq to extract structured resume info
        logger.info(f"Extracting structured resume info using Groq...")
        extracted_resume_data = skill_analysis_service.extract_resume_info(pdf_text)
        
        # Update parsed_meta with extracted data
        parsed_meta = {
            "email": extracted_resume_data.get("contact", {}).get("email"),
            "phone": extracted_resume_data.get("contact", {}).get("phone"),
            "name": extracted_resume_data.get("personal_info", {}).get("name"),
            "location": extracted_resume_data.get("personal_info", {}).get("location"),
            "socials": {
                k: v for k, v in {
                    "linkedin": extracted_resume_data.get("contact", {}).get("linkedin"),
                    "github": extracted_resume_data.get("contact", {}).get("github"),
                    "portfolio": extracted_resume_data.get("contact", {}).get("portfolio")
                }.items() if v
            },
            "education": _normalize_education(extracted_resume_data.get("education", [])),
            "experience": _normalize_experience(extracted_resume_data.get("experience", [])),
            "projects": _normalize_projects(extracted_resume_data.get("projects", [])),
            "skills": extracted_resume_data.get("skills", [])
        }
        
        logger.info(f"✓ Extracted from resume:")
        logger.info(f"  - Name: {parsed_meta.get('name')}")
        logger.info(f"  - Email: {parsed_meta.get('email')}")
        logger.info(f"  - Phone: {parsed_meta.get('phone')}")
        logger.info(f"  - Skills: {len(parsed_meta.get('skills', []))} found")
        logger.info(f"  - Education: {len(parsed_meta.get('education', []))} entries")
        logger.info(f"  - Experience: {len(parsed_meta.get('experience', []))} entries")
        logger.info(f"  - Projects: {len(parsed_meta.get('projects', []))} entries")
        
        resume_path = safe_filename
        resume_text = pdf_text
        
    except Exception as e:
        logger.error(f"Error processing resume: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error processing resume: {str(e)}")

    # Update profile with resume info
    update_payload = {
        "resume_path": resume_path,
        "resume_text": resume_text,
        "resume_last_updated": datetime.utcnow(),
    }
    
    # Update profile fields with extracted data
    if parsed_meta.get("skills"):
        update_payload["skills"] = parsed_meta["skills"]
    if parsed_meta.get("name"):
        update_payload["name"] = parsed_meta["name"]
    if parsed_meta.get("email"):
        update_payload["email"] = parsed_meta["email"]
    if parsed_meta.get("phone"):
        update_payload["phone"] = parsed_meta["phone"]
    if parsed_meta.get("socials"):
        update_payload["socials"] = parsed_meta["socials"]
    if parsed_meta.get("education"):
        update_payload["education"] = parsed_meta["education"]
    if parsed_meta.get("experience"):
        update_payload["experience"] = parsed_meta["experience"]
    if parsed_meta.get("projects"):
        update_payload["projects"] = parsed_meta["projects"]
    if parsed_meta.get("location"):
        update_payload["location"] = parsed_meta["location"]

    updated = db_service.update_profile(profile_id, **update_payload)
    logger.info(f"✓ Profile {profile_id} updated with resume info")
    return ProfileResponse.from_orm(updated)


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(role: str = None, current_user=Depends(get_optional_user)):
    """List all profiles, optionally filtered by role"""
    if role:
        if not job_loader.is_valid_role(role):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {role}"
            )
        profiles = db_service.get_profiles_by_role(role)
    else:
        profiles = db_service.get_all_profiles(user_id=getattr(current_user, "id", None))
    
    return [ProfileResponse.from_orm(p) for p in profiles]

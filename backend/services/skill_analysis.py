"""Service for skill gap analysis and feedback generation using Groq API"""
import os
import json
import logging
from typing import Dict, List, Set, Any
from groq import Groq

logger = logging.getLogger(__name__)


class SkillAnalysisService:
    """Service for analyzing skill gaps and generating feedback with Groq API (Llama 3.3 70B)"""
    
    def __init__(self):
        # Get Groq API key
        self.api_key = os.getenv("GROQ_API_KEY") or ""
        self.model_name = "llama-3.3-70b-versatile"
        self.use_ai = bool(self.api_key)
        
        # Initialize Groq client if API key is available
        if self.use_ai:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
    
    def analyze_gap(self, user_skills: List[str], job_skills: List[str]) -> Dict:
        """
        Analyze skill gap between user and job requirements.
        Returns missing and strong skills.
        """
        user_skills_set = set(s.lower() for s in user_skills)
        job_skills_set = set(s.lower() for s in job_skills)
        
        missing_skills = list(job_skills_set - user_skills_set)
        strong_skills = list(user_skills_set & job_skills_set)
        
        return {
            "missing_skills": sorted(missing_skills),
            "strong_skills": sorted(strong_skills),
            "proficiency": len(strong_skills) / len(job_skills_set) * 100 if job_skills_set else 0
        }
    
    def generate_feedback(self, user_name: str, job_role: str, analysis: Dict) -> str:
        """Generate personalized feedback about strengths and areas to improve"""
        logger.info(f"\n{'='*80}")
        logger.info(f"FEEDBACK GENERATION INITIATED")
        logger.info(f"  user_name: {user_name}")
        logger.info(f"  job_role: {job_role}")
        logger.info(f"  use_ai: {self.use_ai}")
        logger.info(f"  api_key present: {bool(self.api_key)}")
        logger.info(f"  client initialized: {self.client is not None}")
        logger.info(f"{'='*80}")
        try:
            if self.use_ai:
                logger.info("  → Calling AI function (_generate_feedback_ai)")
                return self._generate_feedback_ai(user_name, job_role, analysis)
            else:
                logger.info("  → Calling FALLBACK function (_generate_feedback_fallback)")
                return self._generate_feedback_fallback(user_name, job_role, analysis)
        except Exception as e:
            logger.warning(f"  ✗ AI feedback generation failed: {e}. Using fallback.")
            return self._generate_feedback_fallback(user_name, job_role, analysis)
    
    def _generate_feedback_ai(self, user_name: str, job_role: str, analysis: Dict) -> str:
        """Generate personalized, motivating feedback"""
        logger.info(f"  🤖 INSIDE AI FUNCTION: _generate_feedback_ai()")
        try:
            # Prepare data
            current_skills = analysis.get("strong_skills", [])
            missing_skills = analysis.get("missing_skills", [])
            proficiency = round(analysis.get("proficiency", 0), 1)
            
            current_skills_str = ", ".join(current_skills[:8]) if current_skills else "foundational skills"
            missing_top = ", ".join(missing_skills[:5]) if missing_skills else "advanced techniques"
            
            prompt = f"""You are a thoughtful career mentor helping a learner understand where they stand for a target role.

Learner name: {user_name}
Target role: {job_role}
Current proficiency: {proficiency}%
Strong skills already demonstrated: {current_skills_str}
Most important missing skills: {missing_top}

Write one short paragraph of personalized feedback.

Requirements:
- 45 to 75 words
- Start with a realistic positive observation about the learner's current strengths
- Mention 2 to 3 priority gaps to focus on next
- Sound supportive, practical, and personalized
- Do not use bullet points
- Do not exaggerate readiness
- Do not pad with generic motivational filler

Return only the feedback paragraph."""
            
            logger.info(f"Generating motivating feedback for {user_name}")
            logger.info(f"  Prompt: {prompt[:100]}...")
            
            # Call Groq API
            logger.info(f"  Calling Groq API...")
            message = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=140,
                top_p=0.9
            )
            
            feedback = message.choices[0].message.content.strip()
            logger.info(f"✓ Feedback generated ({len(feedback.split())} words) using Groq Llama 3.3 70B")
            logger.info(f"  Response: {feedback[:100]}...")
            return feedback
        except Exception as e:
            logger.error(f"  ✗ ERROR in _generate_feedback_ai(): {type(e).__name__}: {str(e)}")
            logger.error(f"  Full error details: {e}", exc_info=True)
            raise
    
    def _generate_feedback_fallback(self, user_name: str, job_role: str, analysis: Dict) -> str:
        """Fallback feedback generation using templates"""
        proficiency = round(analysis["proficiency"], 1)
        
        if proficiency >= 80:
            return f"Great work, {user_name}! You're well-prepared for {job_role}. Focus on mastering the remaining skills: {', '.join(analysis['missing_skills'][:3])}."
        elif proficiency >= 50:
            return f"Good progress, {user_name}! You have several relevant skills for {job_role}. Prioritize learning: {', '.join(analysis['missing_skills'][:3])} to strengthen your candidacy."
        else:
            return f"{user_name}, you have potential for {job_role}. Start by building foundational knowledge in: {', '.join(analysis['missing_skills'][:3])}."
    
    def generate_roadmap(self, missing_skills: List[str], user_skills: List[str] = None, job_role: str = None) -> List[Dict]:
        """Generate a structured learning roadmap for missing skills"""
        logger.info(f"\n{'='*80}")
        logger.info(f"ROADMAP GENERATION INITIATED")
        logger.info(f"  missing_skills: {missing_skills[:3]}{'...' if len(missing_skills) > 3 else ''}")
        logger.info(f"  use_ai: {self.use_ai}")
        logger.info(f"  api_key present: {bool(self.api_key)}")
        logger.info(f"  client initialized: {self.client is not None}")
        logger.info(f"{'='*80}")
        try:
            if self.use_ai:
                logger.info("  → Calling AI function (_generate_roadmap_ai)")
                return self._generate_roadmap_ai(missing_skills, user_skills or [], job_role or "target role")
            else:
                logger.info("  → Calling FALLBACK function (_generate_roadmap_fallback)")
                return self._generate_roadmap_fallback(missing_skills)
        except Exception as e:
            logger.warning(f"  ✗ AI roadmap generation failed: {e}. Using fallback.")
            return self._generate_roadmap_fallback(missing_skills)
    
    def _generate_roadmap_ai(self, missing_skills: List[str], user_skills: List[str], job_role: str) -> List[Dict]:
        """Generate progressive learning roadmap starting from what user knows"""
        logger.info(f"  🤖 INSIDE AI FUNCTION: _generate_roadmap_ai()")
        try:
            # Prepare skills
            skills_to_learn = missing_skills if missing_skills else []
            current_base = user_skills if user_skills else ["foundational knowledge"]
            
            skills_str = ", ".join(skills_to_learn) if skills_to_learn else "advanced skills"
            current_str = ", ".join(current_base)
            
            prompt = f"""You are acting like a personal teacher and study coach for a learner preparing for a target role.

Target role: {job_role}
Skills the learner already has: {current_str}
Skills the learner still needs: {skills_str}

Build a highly personalized roadmap that starts from the learner's current base and teaches the missing skills step by step.

Important expectations:
- Use the learner's current skills explicitly when deciding the sequence
- Explain concepts as if the learner has basic knowledge in their existing skills but still needs guided progression into the missing ones
- Include specific learning directions, practice ideas, and useful resource links when possible
- Make the plan feel like a teacher is guiding one person, not a generic syllabus
- Cover the full set of missing skills, grouping them logically if needed

Return ONLY valid JSON as an array with exactly 3 objects and no markdown.

Each object must follow this schema:
[
  {{
    "step": 1,
    "title": "Clear title",
    "timeframe": "X weeks",
    "goal": "What this stage is trying to achieve",
    "why_this_now": "Why this comes first based on the learner's current skills",
    "what_to_learn": ["concept 1", "concept 2", "concept 3"],
    "teacher_explanation": "Short explanation in a personal-teacher tone",
    "resources": [
      {{"name": "resource name", "type": "course/article/video/docs", "url": "https://..."}}
    ],
    "practice_tasks": ["task 1", "task 2"],
    "success_signal": "How the learner will know they are ready for the next step"
  }},
  {{
    "step": 2,
    "title": "Clear title",
    "timeframe": "X weeks",
    "goal": "What this stage is trying to achieve",
    "why_this_now": "Why this comes second",
    "what_to_learn": ["concept 1", "concept 2", "concept 3"],
    "teacher_explanation": "Short explanation in a personal-teacher tone",
    "resources": [
      {{"name": "resource name", "type": "course/article/video/docs", "url": "https://..."}}
    ],
    "practice_tasks": ["task 1", "task 2"],
    "success_signal": "How the learner will know they are ready for the next step"
  }},
  {{
    "step": 3,
    "title": "Clear title",
    "timeframe": "X weeks",
    "goal": "What this stage is trying to achieve",
    "why_this_now": "Why this comes last",
    "what_to_learn": ["concept 1", "concept 2", "concept 3"],
    "teacher_explanation": "Short explanation in a personal-teacher tone",
    "resources": [
      {{"name": "resource name", "type": "course/article/video/docs", "url": "https://..."}}
    ],
    "practice_tasks": ["task 1", "task 2"],
    "success_signal": "How the learner will know they are ready for the next step"
  }}
]

Make sure the 3 steps clearly progress from the current skill base toward {job_role}."""
            
            logger.info(f"Generating progressive learning roadmap")
            logger.info(f"Current base: {current_str}")
            logger.info(f"Skills to learn: {skills_str}")
            logger.info(f"  Calling Groq API...")
            
            # Call Groq API
            message = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1800,
                top_p=0.9
            )
            
            content = message.choices[0].message.content.strip()
            logger.info(f"  Received response ({len(content)} chars)")
            
            # Parse JSON
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            roadmap = json.loads(content)
            
            # Validate
            if not isinstance(roadmap, list) or len(roadmap) != 3:
                logger.warning("Invalid roadmap structure - not a list of 3 items")
                return self._generate_roadmap_fallback(missing_skills)
            
            logger.info("✓ Progressive roadmap generated successfully using Groq Llama 3.3 70B")
            return roadmap
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ JSON parsing error in _generate_roadmap_ai(): {e}")
            logger.error(f"  Content was: {content[:200] if 'content' in locals() else 'N/A'}")
            return self._generate_roadmap_fallback(missing_skills)
        except Exception as e:
            logger.error(f"  ✗ ERROR in _generate_roadmap_ai(): {type(e).__name__}: {str(e)}")
            logger.error(f"  Full error details: {e}", exc_info=True)
            return self._generate_roadmap_fallback(missing_skills)
    
    def _generate_roadmap_fallback(self, missing_skills: List[str]) -> List[Dict]:
        """Fallback roadmap generation using templates"""
        if not missing_skills:
            return [{
                "step": 1,
                "title": "Master Advanced Topics",
                "description": "Deepen knowledge in your current expertise areas."
            }]
        
        top_3_skills = missing_skills[:3]
        roadmap = []
        
        roadmap.append({
            "step": 1,
            "title": f"Learn {top_3_skills[0]}",
            "description": f"Start with fundamentals of {top_3_skills[0]}. Complete online courses and tutorials."
        })
        
        if len(top_3_skills) > 1:
            roadmap.append({
                "step": 2,
                "title": f"Master {top_3_skills[1]}",
                "description": f"Build practical projects using {top_3_skills[1]} to reinforce learning."
            })
        else:
            roadmap.append({
                "step": 2,
                "title": "Build Projects",
                "description": "Create portfolio projects that showcase your {top_3_skills[0]} skills."
            })
        
        if len(top_3_skills) > 2:
            roadmap.append({
                "step": 3,
                "title": f"Practice {top_3_skills[2]}",
                "description": f"Solve real-world problems using {top_3_skills[2]} and contribute to open source."
            })
        else:
            roadmap.append({
                "step": 3,
                "title": "Gain Experience",
                "description": "Apply your skills in real-world projects and seek mentorship."
            })
        
        return roadmap
    
    def extract_resume_info(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract complete structured information from resume using Groq:
        - Skills (all mentioned)
        - Education (school/college, timeline, percentage/CGPA)
        - Experience (company, title, duration, description)
        - Projects (name, description, technologies, duration)
        - Contact info (email, phone, socials)
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"RESUME EXTRACTION INITIATED")
        logger.info(f"  resume_length: {len(resume_text)} chars")
        logger.info(f"  use_ai: {self.use_ai}")
        logger.info(f"  api_key present: {bool(self.api_key)}")
        logger.info(f"  client initialized: {self.client is not None}")
        logger.info(f"{'='*80}")
        try:
            if self.use_ai:
                logger.info("  → Calling AI function (_extract_resume_info_ai)")
                return self._extract_resume_info_ai(resume_text)
            else:
                logger.info("  → Calling FALLBACK function (_extract_resume_info_fallback)")
                return self._extract_resume_info_fallback(resume_text)
        except Exception as e:
            logger.warning(f"  ✗ AI resume extraction failed: {e}. Using fallback.")
            return self._extract_resume_info_fallback(resume_text)
    
    def _extract_resume_info_ai(self, resume_text: str) -> Dict[str, Any]:
        """Use Groq to extract structured resume information"""
        logger.info(f"  🤖 INSIDE AI FUNCTION: _extract_resume_info_ai()")
        try:
            prompt = f"""Extract ALL structured information from this resume and return as JSON.

RESUME TEXT:
{resume_text}

Extract and structure the following (be thorough and capture ALL entries):

1. **Skills** - All technical, professional, and soft skills mentioned
2. **Education** - School/College name, degree, timeline (start-end year or "Month Year - Month Year"), GPA/Percentage/Score (if available)
3. **Experience** - Job title, Company name, Duration (start date - end date), Description of responsibilities (2-3 key points)
4. **Projects** - Project name, Description, Technologies used, Duration/Timeline
5. **Contact** - Email, Phone, LinkedIn, GitHub, Portfolio URLs (if mentioned)
6. **Personal Info** - Name, Location (if available)

**Important Requirements:**
- Return ONLY valid JSON, no markdown, no extra text
- For dates/timeline: Use format "Month Year - Month Year" or "Year - Year" when month not available
- Education format: {{"school": "Name", "degree": "Type", "field": "Field of Study", "timeline": "Start - End", "percentage_or_gpa": "Value"}}
- Experience format: {{"company": "Name", "job_title": "Title", "duration": "Start - End", "description": ["Point 1", "Point 2", "Point 3"]}}
- Projects format: {{"project_name": "Name", "description": "Description", "technologies": ["Tech1", "Tech2"], "duration": "Timeline"}}
- Skills: Return as array of strings, categorized if possible
- Include ALL entries found - be comprehensive

**JSON Structure to return:**
{{
  "personal_info": {{"name": "...", "location": "..."}},
  "contact": {{"email": "...", "phone": "...", "linkedin": "...", "github": "...", "portfolio": "..."}},
  "skills": ["skill1", "skill2", ...],
  "education": [
    {{"school": "...", "degree": "...", "field": "...", "timeline": "...", "percentage_or_gpa": "..."}},
    ...
  ],
  "experience": [
    {{"company": "...", "job_title": "...", "duration": "...", "description": ["...", "...", "..."]}},
    ...
  ],
  "projects": [
    {{"project_name": "...", "description": "...", "technologies": ["...", "..."], "duration": "..."}},
    ...
  ]
}}

Extract EVERYTHING from the resume. Return valid JSON only."""
            
            logger.info("🤖 RESUME EXTRACTION VIA GROQ - Starting comprehensive extraction")
            logger.info(f"  Resume text length: {len(resume_text)} chars")
            logger.info(f"  Calling Groq API...")
            
            # Call Groq API
            message = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temp for factual extraction
                max_tokens=2000,
                top_p=0.9
            )
            
            content = message.choices[0].message.content.strip()
            logger.info(f"  Received response ({len(content)} chars)")
            
            # Parse JSON response
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            extracted = json.loads(content)
            
            # Log what was extracted
            logger.info(f"✓ Resume extracted successfully using Groq Llama 3.3 70B:")
            logger.info(f"  - Skills: {len(extracted.get('skills', []))} found")
            logger.info(f"  - Education: {len(extracted.get('education', []))} entries")
            logger.info(f"  - Experience: {len(extracted.get('experience', []))} entries")
            logger.info(f"  - Projects: {len(extracted.get('projects', []))} entries")
            
            return extracted
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ JSON parsing error in _extract_resume_info_ai(): {e}")
            logger.error(f"  Content was: {content[:200] if 'content' in locals() else 'N/A'}")
            return self._extract_resume_info_fallback(resume_text)
        except Exception as e:
            logger.error(f"  ✗ ERROR in _extract_resume_info_ai(): {type(e).__name__}: {str(e)}")
            logger.error(f"  Full error details: {e}", exc_info=True)
            return self._extract_resume_info_fallback(resume_text)
    
    def _extract_resume_info_fallback(self, resume_text: str) -> Dict[str, Any]:
        """Fallback resume extraction using regex (returns basic structure)"""
        import re
        
        extracted = self._get_empty_resume_structure()
        
        # Extract email
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
        if email_match:
            extracted["contact"]["email"] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r"(\+?\d[\d\-\s]{8,}\d)", resume_text)
        if phone_match:
            extracted["contact"]["phone"] = phone_match.group(0).strip()
        
        # Extract LinkedIn
        linkedin_match = re.search(r"(https?://(?:www\.)?linkedin\.com/[^\s]+)", resume_text, re.IGNORECASE)
        if linkedin_match:
            extracted["contact"]["linkedin"] = linkedin_match.group(0)
        
        # Extract GitHub
        github_match = re.search(r"(https?://(?:www\.)?github\.com/[^\s]+)", resume_text, re.IGNORECASE)
        if github_match:
            extracted["contact"]["github"] = github_match.group(0)
        
        logger.info("✓ Resume extracted using fallback (basic extraction)")
        return extracted
    
    def _get_empty_resume_structure(self) -> Dict[str, Any]:
        """Return empty resume structure template"""
        return {
            "personal_info": {"name": "", "location": ""},
            "contact": {"email": "", "phone": "", "linkedin": "", "github": "", "portfolio": ""},
            "skills": [],
            "education": [],
            "experience": [],
            "projects": []
        }


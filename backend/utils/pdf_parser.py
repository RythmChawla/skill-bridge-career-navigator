"""Utility for parsing PDF documents and extracting text"""
import re
import logging
from typing import List, Set
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file with error handling"""
    try:
        reader = PdfReader(pdf_path)
        
        if len(reader.pages) == 0:
            raise ValueError("PDF file is empty or has no readable pages")
        
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if not page_text or not page_text.strip():
                    logger.warning(f"No text extracted from page {page_num + 1}")
                text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                continue
        
        if not text.strip():
            raise ValueError("Could not extract any text from PDF. The PDF might be image-based (scanned). Please upload a resume with selectable text.")
        
        return text
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


# Predefined skill list for keyword matching (sorted by length desc for better matching)
AVAILABLE_SKILLS = {
    "Machine Learning", "Deep Learning", "React Native", "Spring Boot", "Graph QL",
    "Integration Testing", "E2E Testing", "Unit Testing", "Load Balancing",
    "AWS Lambda", "AWS RDS", "AWS S3", "AWS EC2", "GitHub Actions",
    "GitHub", "GitLab", "Python", "JavaScript", "TypeScript", "Java", "C++", 
    "C#", "Go", "Rust", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", 
    "Elasticsearch", "React", "Vue", "Angular", "Svelte", "Next.js",
    "Node.js", "Express", "FastAPI", "Django", "Flask",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform",
    "Git", "CI/CD", "Jenkins", "REST", "GraphQL", "WebSocket", "API", "HTTP", "HTTPS",
    "Linux", "Unix", "Windows", "macOS", "Shell", "Bash",
    "HTML", "CSS", "SCSS", "Webpack", "Vite", "Babel",
    "TensorFlow", "PyTorch", "Scikit-learn", "Data Science", "Statistics", 
    "Pandas", "NumPy", "Matplotlib", "Jupyter", "Android", "iOS", "Swift", 
    "Kotlin", "Flutter", "DevOps", "SRE", "Monitoring", "Logging", "Datadog", 
    "Prometheus", "Agile", "Scrum", "JIRA", "Confluence", "Slack",
    "Security", "OAuth", "JWT", "Encryption", "SSL",
    "Performance", "Caching", "Scaling", "Optimization", "Testing", "Jest", "Pytest"
}


def extract_skills_section(text: str) -> str:
    """Try to extract skills section from resume, fallback to full text"""
    # Look for section headers like "SKILLS", "Technical Skills", etc.
    patterns = [
        r'(?:SKILLS|Skills|TECHNICAL\s+SKILLS|Technical\s+Skills)[\s\n]*:?[\s\n]*([^A-Z]*?)(?=(?:EXPERIENCE|Experience|EDUCATION|Education|PROJECTS|Projects|CERTIFICATIONS|Certifications|$))',
        r'(?:##|###)?\s*(?:SKILLS|Skills|TECHNICAL\s+SKILLS|Technical\s+Skills)[\s\n]*:?[\s\n]*([^#]*?)(?=(?:##|###|EXPERIENCE|Experience|EDUCATION|Education|PROJECTS|Projects))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            skills_section = match.group(1)
            if skills_section.strip():
                logger.info("Found dedicated skills section in resume")
                return skills_section
    
    logger.info("No dedicated skills section found, using full resume text")
    return text


def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using intelligent keyword matching"""
    if not text or not text.strip():
        logger.warning("Empty text provided to extract_skills_from_text")
        return []
    
    # Try to extract skills section first
    skills_text = extract_skills_section(text)
    text_lower = skills_text.lower()
    
    extracted_skills: Set[str] = set()
    
    # Sort skills by length (longest first) to avoid partial matches
    # e.g., match "Machine Learning" before "Learning"
    sorted_skills = sorted(AVAILABLE_SKILLS, key=len, reverse=True)
    
    for skill in sorted_skills:
        skill_lower = skill.lower()
        # Use word boundary matching to avoid partial matches
        # e.g., "React" shouldn't match "Reacted"
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            extracted_skills.add(skill)
    
    result = list(extracted_skills)
    logger.info(f"Extracted {len(result)} skills from resume: {result}")
    
    return result

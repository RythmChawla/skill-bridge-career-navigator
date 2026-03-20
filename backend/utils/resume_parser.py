"""Lightweight resume parsing helper with optional pydparser."""
import re
import json
from typing import Dict, Any, List, Optional


def try_import_pydparser():
    try:
        from pydparser import ResumeParser  # type: ignore
        return ResumeParser
    except Exception:
        return None


def regex_extract(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}

    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email_match:
        data["email"] = email_match.group(0)

    phone_match = re.search(r"(\+?\d[\d\-\s]{8,}\d)", text)
    if phone_match:
        data["phone"] = phone_match.group(0).strip()

    linkedins = re.findall(r"(https?://(?:www\.)?linkedin\.com/[^\s]+)", text, re.IGNORECASE)
    githubs = re.findall(r"(https?://(?:www\.)?github\.com/[^\s]+)", text, re.IGNORECASE)
    if linkedins or githubs:
        data["socials"] = {}
        if linkedins:
            data["socials"]["linkedin"] = linkedins[0]
        if githubs:
            data["socials"]["github"] = githubs[0]

    # crude section splits
    sections = re.split(r"\n(?=[A-Z][A-Za-z ]{2,30}:?)", text)
    experience = []
    projects = []
    education = []
    for sec in sections:
        header = sec.split("\n", 1)[0].lower()
        if "experience" in header or "intern" in header or "work" in header:
            lines = [l.strip("•- \t") for l in sec.split("\n")[1:] if l.strip()]
            for l in lines:
                if len(l) > 3:
                    experience.append({"bullet": l})
        if "project" in header:
            lines = [l.strip("•- \t") for l in sec.split("\n")[1:] if l.strip()]
            for l in lines:
                projects.append({"bullet": l})
        if "education" in header or "university" in header or "college" in header or "degree" in header:
            lines = [l.strip("•- \t") for l in sec.split("\n")[1:] if l.strip()]
            for l in lines:
                education.append({"bullet": l})
    if experience:
        data["experience"] = experience
    if projects:
        data["projects"] = projects
    if education:
        data["education"] = education

    return data


def parse_resume(file_path: str, text: Optional[str] = None) -> Dict[str, Any]:
    """Return parsed fields using pydparser if available, else regex. If text provided, use it for fallback parsing."""
    ResumeParser = try_import_pydparser()
    if ResumeParser:
        try:
            parsed = ResumeParser(file_path).get_extracted_data() or {}
            return {
                "name": parsed.get("name"),
                "email": parsed.get("email"),
                "phone": parsed.get("mobile_number"),
                "skills": parsed.get("skills") or [],
                "experience": parsed.get("experience") or [],
                "education": parsed.get("education") or [],
                "total_experience": parsed.get("total_experience"),
                "socials": {
                    k: v for k, v in {
                        "linkedin": parsed.get("linkedin"),
                        "github": parsed.get("github")
                    }.items() if v
                }
            }
        except Exception:
            pass
    # Fallback
    if text is None:
        try:
            with open(file_path, "r", errors="ignore") as f:
                text = f.read()
        except Exception:
            text = ""
    return regex_extract(text or "")

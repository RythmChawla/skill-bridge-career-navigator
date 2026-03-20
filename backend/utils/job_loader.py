"""Load and manage job roles dataset"""
import csv
from typing import Dict, List, Set
import os


class JobLoader:
    """Load job roles and required skills from CSV"""
    
    def __init__(self, csv_path: str = "all_job_post.csv"):
        self.csv_path = csv_path
        self.jobs: Dict[str, Set[str]] = {}
        self.load_jobs()
    
    def load_jobs(self):
        """Load jobs from CSV file"""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"jobs.csv not found at {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # dataset columns: Job Title, Job Description, job_skill_set, Certifications
                    role = (row.get('Job Title') or '').strip()
                    skill_raw = row.get('job_skill_set') or ''
                    if not role:
                        continue
                    skills = {s.strip() for s in skill_raw.split(',') if s.strip()}

                    # Merge duplicate roles across companies by unioning skills
                    if role in self.jobs:
                        self.jobs[role].update(skills)
                    else:
                        self.jobs[role] = skills
        except Exception as e:
            raise ValueError(f"Failed to load all_job_post.csv: {str(e)}")
    
    def get_job_roles(self) -> List[str]:
        """Get list of all available job roles"""
        return list(self.jobs.keys())
    
    def get_job_skills(self, role: str) -> Set[str]:
        """Get required skills for a specific role"""
        if role not in self.jobs:
            raise ValueError(f"Role '{role}' not found in job database")
        return self.jobs[role].copy()
    
    def is_valid_role(self, role: str) -> bool:
        """Check if role exists in database"""
        return role in self.jobs

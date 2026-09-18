import re
from typing import List, Dict, Set
from app.services.analyzer_service import TECHNICAL_SKILLS, ResumeAnalyzerService
from app.services.nlp_service import NLPService


class JobMatcherService:
    @staticmethod
    def match_resume_to_job(resume_text: str, job_description: str) -> dict:
        # Extract skills from resume
        resume_skills = set(ResumeAnalyzerService._extract_skills(resume_text))

        # Extract technical skills required by job description
        job_skills = set(ResumeAnalyzerService._extract_skills(job_description))

        # Extract general important technical terms from job description
        job_words = set(re.findall(r'\b[a-zA-Z0-9+#.-]+\b', job_description.lower()))
        resume_words = set(re.findall(r'\b[a-zA-Z0-9+#.-]+\b', resume_text.lower()))

        # Match calculation
        if job_skills:
            matching_skills = list(resume_skills.intersection(job_skills))
            missing_skills = list(job_skills.difference(resume_skills))
            skill_match_ratio = len(matching_skills) / len(job_skills)
        else:
            matching_skills = list(resume_skills)
            missing_skills = []
            skill_match_ratio = 0.5

        # Word overlap score for general keywords
        common_words = resume_words.intersection(job_words)
        stop_words = {"and", "the", "with", "for", "in", "to", "of", "a", "an", "is", "are", "you", "we", "our", "work", "job", "role"}
        meaningful_common = common_words.difference(stop_words)
        
        # Combined score calculation
        match_percentage = round((skill_match_ratio * 0.7 + min(len(meaningful_common) / 30.0, 1.0) * 0.3) * 100, 1)
        match_percentage = min(100.0, max(0.0, match_percentage))

        # Suggested improvements based on job match
        suggested_improvements = []
        if missing_skills:
            suggested_improvements.append(
                f"Add experience or projects demonstrating: {', '.join(missing_skills[:4])}."
            )
        
        if "docker" in job_description.lower() and "Docker" not in resume_skills:
            suggested_improvements.append("Highlight Docker containerization or deployment pipeline experience.")

        if "aws" in job_description.lower() and "AWS" not in resume_skills:
            suggested_improvements.append("Mention cloud infrastructure or AWS service usage if applicable.")

        if match_percentage < 60.0:
            suggested_improvements.append("Align project bullet points to mirror key phrases and technology keywords from this specific job description.")

        if not suggested_improvements:
            suggested_improvements.append("Your resume matches this job description exceptionally well!")

        summary = (
            f"Match rate: {match_percentage}%. "
            f"Found {len(matching_skills)} matching core skills out of {len(job_skills)} required."
        )

        return {
            "match_percentage": match_percentage,
            "matching_skills": sorted(matching_skills),
            "missing_keywords": sorted(missing_skills),
            "suggested_improvements": suggested_improvements,
            "summary": summary
        }

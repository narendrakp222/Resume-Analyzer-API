import re
from typing import List, Dict, Set, Tuple
from app.services.nlp_service import NLPService

# Taxonomy of Technical Skills
TECHNICAL_SKILLS = {
    # Languages
    "Python": [r"\bpython\b", r"\bpython3\b"],
    "Java": [r"\bjava\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "SQL": [r"\bsql\b"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "Go": [r"\bgolang\b", r"\bgo\b"],
    "Rust": [r"\brust\b"],
    "HTML": [r"\bhtml5?\b"],
    "CSS": [r"\bcss3?\b"],
    "PHP": [r"\bphp\b"],
    "Ruby": [r"\bruby\b"],
    "C#": [r"\bc#\b", r"\bcsharp\b"],

    # Frameworks & Libraries
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "React": [r"\breact(?:\.js)?\b"],
    "Next.js": [r"\bnext(?:\.js)?\b"],
    "Vue.js": [r"\bvue(?:\.js)?\b"],
    "Angular": [r"\bangular\b"],
    "Node.js": [r"\bnode(?:\.js)?\b"],
    "Express": [r"\bexpress(?:\.js)?\b"],
    "Spring Boot": [r"\bspring\s*boot\b", r"\bspring\b"],
    "Tailwind": [r"\btailwind(?:\s*css)?\b"],

    # Databases
    "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "Redis": [r"\bredis\b"],
    "SQLite": [r"\bsqlite3?\b"],

    # DevOps & Cloud
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "AWS": [r"\baws\b", r"\bamazon\s*web\s*services\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle\s*cloud\b"],
    "Azure": [r"\bazure\b"],
    "Git": [r"\bgit\b"],
    "GitHub": [r"\bgithub\b"],
    "GitLab": [r"\bgitlab\b"],
    "CI/CD": [r"\bci[\/\s]*cd\b", r"\bcontinuous\s*integration\b"],
    "Linux": [r"\blinux\b", r"\bubuntu\b", r"\bbash\b"],

    # Architecture & AI/ML
    "REST API": [r"\brestful\b", r"\brest\s*api\b", r"\brest\b"],
    "GraphQL": [r"\bgraphql\b"],
    "Microservices": [r"\bmicroservices?\b"],
    "Machine Learning": [r"\bmachine\s*learning\b", r"\bml\b"],
    "PyTorch": [r"\bpytorch\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "Scikit-learn": [r"\bscikit-learn\b", r"\bsklearn\b"],
    "spaCy": [r"\bspacy\b"],
    "NLP": [r"\bnlp\b", r"\bnatural\s*language\s*processing\b"],
}

# Essential Software Engineering Skills for Internships
CORE_INTERNSHIP_SKILLS = [
    "Python", "Java", "JavaScript", "SQL", "PostgreSQL",
    "FastAPI", "React", "Docker", "Git", "GitHub",
    "AWS", "REST API", "Machine Learning"
]


class ResumeAnalyzerService:
    @staticmethod
    def analyze(resume_text: str) -> dict:
        text_lower = resume_text.lower()

        # 1. Extract Skills
        extracted_skills = ResumeAnalyzerService._extract_skills(resume_text)

        # 2. Missing Skills Detection
        missing_skills = [
            skill for skill in CORE_INTERNSHIP_SKILLS if skill not in extracted_skills
        ]

        # 3. Keyword Count
        target_keywords = set(TECHNICAL_SKILLS.keys())
        keyword_count = NLPService.calculate_keyword_frequencies(resume_text, target_keywords)

        # 4. Check Presence of Key Resume Components
        has_contact_info = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text))
        has_phone = bool(re.search(r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', resume_text))
        has_github = "github.com" in text_lower or "github" in text_lower
        has_linkedin = "linkedin.com" in text_lower or "linkedin" in text_lower

        has_education = any(k in text_lower for k in ["education", "university", "bachelor", "b.s", "b.tech", "degree"])
        has_projects = any(k in text_lower for k in ["projects", "project", "personal projects", "key projects"])
        has_experience = any(k in text_lower for k in ["experience", "work experience", "internship", "employment"])

        # Check for quantified metrics (e.g. 50%, $10k, 300ms, 10x, 500+ users)
        quantified_metrics = re.findall(r'\b(?:\d+%\b|\$\d+\b|\b\d+(?:ms|s|x|k|\+)\b|\b\d+\s*(?:users|clients|requests|speedup|improvement|latency|reduction)\b)', text_lower)
        has_metrics = len(quantified_metrics) >= 2

        # 5. Calculate ATS Score (0 to 100)
        ats_score, scoring_breakdown = ResumeAnalyzerService._calculate_ats_score(
            extracted_skills=extracted_skills,
            has_contact_info=has_contact_info,
            has_github=has_github,
            has_linkedin=has_linkedin,
            has_education=has_education,
            has_projects=has_projects,
            has_experience=has_experience,
            has_metrics=has_metrics,
            keyword_count=keyword_count
        )

        # 6. Suggestions Engine
        suggestions = ResumeAnalyzerService._generate_suggestions(
            extracted_skills=extracted_skills,
            has_github=has_github,
            has_linkedin=has_linkedin,
            has_projects=has_projects,
            has_metrics=has_metrics,
            missing_skills=missing_skills,
            ats_score=ats_score
        )

        # 7. Resume Summary
        summary = (
            f"Resume contains {len(extracted_skills)} technical skills identified. "
            f"ATS Score is {ats_score}/100 based on contact info, sections, metrics, and technical keyword density."
        )

        return {
            "ats_score": ats_score,
            "extracted_skills": extracted_skills,
            "missing_skills": missing_skills,
            "keyword_count": keyword_count,
            "suggestions": suggestions,
            "summary": summary
        }

    @staticmethod
    def _extract_skills(resume_text: str) -> List[str]:
        found_skills = []
        for skill_name, patterns in TECHNICAL_SKILLS.items():
            for pattern in patterns:
                if re.search(pattern, resume_text, re.IGNORECASE):
                    found_skills.append(skill_name)
                    break
        return found_skills

    @staticmethod
    def _calculate_ats_score(
        extracted_skills: List[str],
        has_contact_info: bool,
        has_github: bool,
        has_linkedin: bool,
        has_education: bool,
        has_projects: bool,
        has_experience: bool,
        has_metrics: bool,
        keyword_count: Dict[str, int]
    ) -> Tuple[int, Dict[str, int]]:
        score = 0
        breakdown = {}

        # 1. Contact Information & Links (Max 15 pts)
        contact_pts = 0
        if has_contact_info: contact_pts += 5
        if has_github: contact_pts += 5
        if has_linkedin: contact_pts += 5
        score += contact_pts
        breakdown["contact_info"] = contact_pts

        # 2. Key Sections (Max 20 pts)
        sections_pts = 0
        if has_education: sections_pts += 7
        if has_projects: sections_pts += 7
        if has_experience: sections_pts += 6
        score += sections_pts
        breakdown["sections"] = sections_pts

        # 3. Technical Skills Count & Diversity (Max 30 pts)
        skills_count = len(extracted_skills)
        if skills_count >= 10:
            skills_pts = 30
        elif skills_count >= 6:
            skills_pts = 22
        elif skills_count >= 3:
            skills_pts = 14
        else:
            skills_pts = 5
        score += skills_pts
        breakdown["skills"] = skills_pts

        # 4. Quantified Project Impact Metrics (Max 20 pts)
        metrics_pts = 20 if has_metrics else 5
        score += metrics_pts
        breakdown["metrics"] = metrics_pts

        # 5. Technical Keyword Density (Max 15 pts)
        total_kw_mentions = sum(keyword_count.values())
        if total_kw_mentions >= 15:
            kw_pts = 15
        elif total_kw_mentions >= 8:
            kw_pts = 10
        elif total_kw_mentions >= 3:
            kw_pts = 5
        else:
            kw_pts = 2
        score += kw_pts
        breakdown["keyword_density"] = kw_pts

        final_score = min(100, max(0, score))
        return final_score, breakdown

    @staticmethod
    def _generate_suggestions(
        extracted_skills: List[str],
        has_github: bool,
        has_linkedin: bool,
        has_projects: bool,
        has_metrics: bool,
        missing_skills: List[str],
        ats_score: int
    ) -> List[str]:
        suggestions = []

        if not has_github:
            suggestions.append("Add a clear GitHub profile link in your contact header to showcase open-source projects.")
        
        if not has_linkedin:
            suggestions.append("Add your LinkedIn profile URL to build professional credibility.")

        if not has_metrics:
            suggestions.append("Add quantified project impact (e.g., 'Reduced API latency by 35%', 'Served 10k+ active users', 'Improved query performance by 40%').")

        if not has_projects:
            suggestions.append("Include a dedicated 'Projects' section highlighting full-stack or backend software engineering applications.")

        if "Docker" not in extracted_skills:
            suggestions.append("Include Docker and containerization experience to strengthen backend internship fit.")

        if "Git" not in extracted_skills and "GitHub" not in extracted_skills:
            suggestions.append("Explicitly mention Git version control in your Skills or Experience section.")

        if missing_skills:
            top_missing = ", ".join(missing_skills[:3])
            suggestions.append(f"Consider learning or adding key industry skills like: {top_missing}.")

        if ats_score < 70:
            suggestions.append("Improve technical keyword density by detailing specific tools, frameworks, and database engines used in projects.")

        if not suggestions:
            suggestions.append("Great job! Your resume meets high software engineering internship ATS standards.")

        return suggestions

"""
Gap analysis for identifying resume weaknesses.
"""

import re
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Gap:
    type: str
    severity: str  # 'high', 'medium', 'low'
    description: str
    suggestion: str


class GapAnalyzer:
    """Analyze resume for gaps and ATS issues."""

    # ATS-unfriendly elements
    ATS_BLOCKERS = [
        (
            r"[\u2022\u2023\u25E6\u2043\u2219]",
            "Fancy bullet points",
            "Use standard hyphens (-) or asterisks (*) instead",
        ),
        (r"[│┃┆┇┊┋]", "Table borders/lines", "Convert tables to plain text format"),
        (r"[\u2500-\u257F]", "Box drawing characters", "Remove decorative borders"),
        (r"[\U0001F300-\U0001F9FF]", "Emojis", "Remove emojis from resume"),
    ]

    def __init__(self):
        pass

    def analyze(
        self, parsed_resume, jd_skills: List[str], cv_skills: List[str]
    ) -> Dict:
        """Perform comprehensive gap analysis."""
        gaps = []

        # 1. Employment gaps
        gaps.extend(self._find_employment_gaps(parsed_resume.experiences))

        # 2. Skill gaps
        gaps.extend(self._find_skill_gaps(cv_skills, jd_skills))

        # 3. Formatting issues
        gaps.extend(self._find_formatting_issues(parsed_resume.raw_text))

        # 4. ATS blockers
        gaps.extend(self._find_ats_blockers(parsed_resume.raw_text))

        # 5. Content quality issues
        gaps.extend(self._find_content_issues(parsed_resume))

        # 6. Quantification gaps
        gaps.extend(self._find_quantification_gaps(parsed_resume.experiences))

        return {
            "gaps": gaps,
            "high_priority": [g for g in gaps if g.severity == "high"],
            "medium_priority": [g for g in gaps if g.severity == "medium"],
            "low_priority": [g for g in gaps if g.severity == "low"],
            "total_issues": len(gaps),
        }

    def _find_employment_gaps(self, experiences: List) -> List[Gap]:
        """Detect gaps between jobs."""
        gaps = []

        # Sort by date (most recent first)
        dated_exp = []
        for exp in experiences:
            if exp.end_date:
                dated_exp.append(exp)

        # Check for current employment
        has_current = any(exp.is_current for exp in experiences)
        if not has_current and experiences:
            gaps.append(
                Gap(
                    type="employment",
                    severity="medium",
                    description="No current employment indicated",
                    suggestion='If currently employed, mark your latest role as "Present" or add your current position',
                )
            )

        # Simplified gap detection (would need date parsing for real analysis)
        if len(experiences) > 0 and len(experiences) < 2:
            gaps.append(
                Gap(
                    type="employment",
                    severity="low",
                    description="Limited work history shown",
                    suggestion="Consider adding more relevant experience, internships, or projects",
                )
            )

        return gaps

    def _find_skill_gaps(self, cv_skills: List[str], jd_skills: List[str]) -> List[Gap]:
        """Identify missing required skills."""
        gaps = []

        cv_set = {s.lower() for s in cv_skills}
        jd_set = {s.lower() for s in jd_skills}

        missing = jd_set - cv_set

        if len(missing) > len(jd_set) * 0.5:
            gaps.append(
                Gap(
                    type="skills",
                    severity="high",
                    description=f"Missing {len(missing)} of {len(jd_set)} required skills",
                    suggestion=f"Add these skills if you have them: {', '.join(list(missing)[:5])}",
                )
            )
        elif len(missing) > 0:
            gaps.append(
                Gap(
                    type="skills",
                    severity="medium",
                    description=f"{len(missing)} required skills not explicitly listed",
                    suggestion=f"Consider adding: {', '.join(list(missing)[:3])}",
                )
            )

        return gaps

    def _find_formatting_issues(self, text: str) -> List[Gap]:
        """Check for formatting problems."""
        gaps = []

        # Check length
        word_count = len(text.split())
        if word_count < 200:
            gaps.append(
                Gap(
                    type="formatting",
                    severity="high",
                    description="Resume is too short",
                    suggestion="Add more details about your experience, skills, and achievements",
                )
            )
        elif word_count > 1500:
            gaps.append(
                Gap(
                    type="formatting",
                    severity="medium",
                    description="Resume may be too long",
                    suggestion="Consider condensing to 1-2 pages by removing older or less relevant content",
                )
            )

        # Check for sections
        sections_found = []
        for section in ["experience", "education", "skills"]:
            if re.search(section, text.lower()):
                sections_found.append(section)

        missing_sections = {"experience", "education", "skills"} - set(sections_found)
        if missing_sections:
            gaps.append(
                Gap(
                    type="formatting",
                    severity="high",
                    description=f"Missing essential sections: {', '.join(missing_sections)}",
                    suggestion="Add clear section headers for Experience, Education, and Skills",
                )
            )

        return gaps

    def _find_ats_blockers(self, text: str) -> List[Gap]:
        """Find elements that may break ATS parsing."""
        gaps = []

        for pattern, name, fix in self.ATS_BLOCKERS:
            if re.search(pattern, text):
                gaps.append(
                    Gap(
                        type="ats",
                        severity="medium",
                        description=f"Found {name} which may confuse ATS",
                        suggestion=fix,
                    )
                )

        # Check for headers/footers (page numbers)
        if re.search(r"page\s*\d+\s*of\s*\d+", text.lower()):
            gaps.append(
                Gap(
                    type="ats",
                    severity="low",
                    description="Contains page numbers",
                    suggestion="Remove page numbers for single-page resumes",
                )
            )

        return gaps

    def _find_content_issues(self, parsed_resume) -> List[Gap]:
        """Check content quality."""
        gaps = []

        # Check contact info
        if not parsed_resume.contact.email:
            gaps.append(
                Gap(
                    type="content",
                    severity="high",
                    description="No email address found",
                    suggestion="Add a professional email address",
                )
            )

        if not parsed_resume.contact.phone:
            gaps.append(
                Gap(
                    type="content",
                    severity="medium",
                    description="No phone number found",
                    suggestion="Add a phone number for recruiters to contact you",
                )
            )

        # Check skills section
        if len(parsed_resume.skills) < 5:
            gaps.append(
                Gap(
                    type="content",
                    severity="medium",
                    description="Skills section appears sparse",
                    suggestion="List at least 8-12 relevant technical and soft skills",
                )
            )

        return gaps

    def _find_quantification_gaps(self, experiences: List) -> List[Gap]:
        """Check for quantified achievements."""
        gaps = []

        total_bullets = 0
        quantified_bullets = 0

        for exp in experiences:
            for bullet in exp.bullets:
                total_bullets += 1
                # Check for numbers, percentages, dollar amounts
                if re.search(
                    r"\d+%|\$[\d,]+|\d+\+?(?:\s+(?:users|customers|clients|projects|team|people))",
                    bullet,
                ):
                    quantified_bullets += 1

        if total_bullets > 0:
            ratio = quantified_bullets / total_bullets
            if ratio < 0.3:
                gaps.append(
                    Gap(
                        type="quantification",
                        severity="high",
                        description=f"Only {quantified_bullets}/{total_bullets} bullets contain metrics",
                        suggestion='Add numbers to your achievements: "Increased sales by X%", "Managed team of X", "Reduced costs by $X"',
                    )
                )
            elif ratio < 0.5:
                gaps.append(
                    Gap(
                        type="quantification",
                        severity="medium",
                        description="More quantified achievements would strengthen your resume",
                        suggestion="Try to quantify at least 50% of your bullet points",
                    )
                )

        return gaps

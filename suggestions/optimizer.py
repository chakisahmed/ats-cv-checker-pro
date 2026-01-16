"""
ATS optimization recommendations.
"""

from typing import List, Dict


class ATSOptimizer:
    """Generate ATS optimization recommendations."""

    # ATS best practices
    BEST_PRACTICES = [
        {
            "category": "File Format",
            "tips": [
                "Use .docx or .pdf format (prefer .docx for maximum compatibility)",
                "Avoid scanned documents or image-based PDFs",
                "Use a simple, single-column layout",
            ],
        },
        {
            "category": "Section Headers",
            "tips": [
                "Use standard section names: Experience, Education, Skills",
                'Avoid creative headers like "Where I\'ve Been" instead of "Experience"',
                "Keep headers simple and recognizable",
            ],
        },
        {
            "category": "Formatting",
            "tips": [
                "Use standard fonts (Arial, Calibri, Times New Roman)",
                "Avoid tables, text boxes, and multi-column layouts",
                "Use simple bullet points (•, -, or *)",
                "Avoid headers and footers",
            ],
        },
        {
            "category": "Content",
            "tips": [
                'Spell out acronyms at least once (e.g., "Search Engine Optimization (SEO)")',
                "Include both the acronym and full name for certifications",
                "Use keywords exactly as they appear in the job description",
                "Avoid using images or graphics for important information",
            ],
        },
    ]

    def __init__(self):
        pass

    def get_optimization_tips(self, gaps: Dict, score: float) -> List[Dict]:
        """Get personalized optimization tips based on analysis."""
        tips = []

        # Add general tips first
        for practice in self.BEST_PRACTICES:
            tips.append(
                {
                    "category": practice["category"],
                    "tips": practice["tips"],
                    "priority": "general",
                }
            )

        # Add specific tips based on gaps
        gap_list = gaps.get("gaps", [])

        for gap in gap_list:
            if gap.type == "ats":
                tips.insert(
                    0,
                    {
                        "category": "Critical ATS Issue",
                        "tips": [gap.suggestion],
                        "priority": "high",
                    },
                )
            elif gap.type == "formatting":
                tips.insert(
                    1,
                    {
                        "category": "Formatting Issue",
                        "tips": [gap.suggestion],
                        "priority": "medium",
                    },
                )

        return tips

    def generate_checklist(self) -> List[Dict]:
        """Generate pre-submission ATS checklist."""
        return [
            {"item": "File is .docx or simple .pdf format", "critical": True},
            {"item": "No tables, text boxes, or graphics", "critical": True},
            {"item": "Standard section headers used", "critical": True},
            {"item": "Contact info at top (not in header)", "critical": True},
            {"item": "No fancy bullet points or symbols", "critical": False},
            {"item": "Keywords from job description included", "critical": True},
            {"item": "Dates are in consistent format", "critical": False},
            {"item": "No spelling or grammar errors", "critical": True},
            {"item": "Skills section is comprehensive", "critical": False},
            {"item": "Achievements are quantified where possible", "critical": False},
        ]

    def score_ats_friendliness(self, parsed_resume, gaps: Dict) -> Dict:
        """Score resume's ATS-friendliness specifically."""
        score = 100
        issues = []

        # Check for ATS blockers
        ats_gaps = [g for g in gaps.get("gaps", []) if g.type == "ats"]
        score -= len(ats_gaps) * 10
        issues.extend([g.description for g in ats_gaps])

        # Check for proper sections
        required_sections = ["experience", "education", "skills"]
        for section in required_sections:
            if (
                section not in parsed_resume.sections
                or not parsed_resume.sections[section]
            ):
                score -= 15
                issues.append(f"Missing {section} section")

        # Check contact info
        if not parsed_resume.contact.email:
            score -= 10
            issues.append("No email found")

        return {
            "ats_score": max(0, score),
            "issues": issues,
            "recommendation": "Excellent ATS compatibility"
            if score >= 90
            else "Good ATS compatibility"
            if score >= 70
            else "Needs ATS optimization",
        }

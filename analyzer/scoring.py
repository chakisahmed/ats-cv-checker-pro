"""
Advanced 6-component ATS scoring.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ScoreComponent:
    name: str
    score: float  # 0-100
    weight: float
    details: str


class AdvancedScorer:
    """Calculate comprehensive ATS compatibility score."""

    # Score component weights
    WEIGHTS = {
        "keyword_match": 0.20,
        "semantic_match": 0.20,
        "skill_taxonomy": 0.20,
        "experience_alignment": 0.15,
        "formatting_quality": 0.15,
        "quantification": 0.10,
    }

    def __init__(self):
        pass

    def calculate_score(
        self,
        keyword_result: Dict,
        semantic_score: float,
        skill_coverage: Dict,
        experience_relevance: List[Dict],
        gaps: Dict,
        parsed_resume,
    ) -> Dict:
        """Calculate comprehensive ATS score."""

        components = []

        # 1. Keyword Match (20%)
        keyword_score = keyword_result.get("score", 0) * 100
        components.append(
            ScoreComponent(
                name="Keyword Match",
                score=keyword_score,
                weight=self.WEIGHTS["keyword_match"],
                details=f"{len(keyword_result.get('matching', []))} keywords matched",
            )
        )

        # 2. Semantic Match (20%)
        semantic_pct = semantic_score * 100
        components.append(
            ScoreComponent(
                name="Semantic Match",
                score=semantic_pct,
                weight=self.WEIGHTS["semantic_match"],
                details=f"Content relevance: {semantic_pct:.0f}%",
            )
        )

        # 3. Skill Taxonomy (20%)
        taxonomy_score = skill_coverage.get("coverage_score", 0) * 100
        components.append(
            ScoreComponent(
                name="Skill Coverage",
                score=taxonomy_score,
                weight=self.WEIGHTS["skill_taxonomy"],
                details=f"{len(skill_coverage.get('direct_matches', []))} direct + {len(skill_coverage.get('taxonomy_matches', []))} related skills",
            )
        )

        # 4. Experience Alignment (15%)
        if experience_relevance:
            avg_relevance = sum(e["relevance"] for e in experience_relevance) / len(
                experience_relevance
            )
            exp_score = avg_relevance * 100
        else:
            exp_score = 50  # Default if no experience bullets analyzed
        components.append(
            ScoreComponent(
                name="Experience Alignment",
                score=exp_score,
                weight=self.WEIGHTS["experience_alignment"],
                details=f"Experience relevance to role",
            )
        )

        # 5. Formatting Quality (15%)
        formatting_issues = len(
            [g for g in gaps.get("gaps", []) if g.type in ("formatting", "ats")]
        )
        if formatting_issues == 0:
            format_score = 100
        elif formatting_issues <= 2:
            format_score = 75
        elif formatting_issues <= 4:
            format_score = 50
        else:
            format_score = 25
        components.append(
            ScoreComponent(
                name="Formatting Quality",
                score=format_score,
                weight=self.WEIGHTS["formatting_quality"],
                details=f"{formatting_issues} formatting issues found",
            )
        )

        # 6. Quantification (10%)
        quant_issues = [g for g in gaps.get("gaps", []) if g.type == "quantification"]
        if not quant_issues:
            quant_score = 100
        elif any(g.severity == "high" for g in quant_issues):
            quant_score = 30
        else:
            quant_score = 60
        components.append(
            ScoreComponent(
                name="Quantification",
                score=quant_score,
                weight=self.WEIGHTS["quantification"],
                details="Achievement metrics in bullets",
            )
        )

        # Calculate weighted overall score
        overall_score = sum(c.score * c.weight for c in components)

        # Determine grade
        if overall_score >= 85:
            grade = "A"
            grade_label = "Excellent"
        elif overall_score >= 70:
            grade = "B"
            grade_label = "Good"
        elif overall_score >= 55:
            grade = "C"
            grade_label = "Fair"
        elif overall_score >= 40:
            grade = "D"
            grade_label = "Needs Work"
        else:
            grade = "F"
            grade_label = "Poor Match"

        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "grade_label": grade_label,
            "components": [
                {
                    "name": c.name,
                    "score": round(c.score, 1),
                    "weight": c.weight,
                    "weighted_score": round(c.score * c.weight, 1),
                    "details": c.details,
                }
                for c in components
            ],
            "breakdown": {
                "keyword_match": round(keyword_score, 1),
                "semantic_match": round(semantic_pct, 1),
                "skill_taxonomy": round(taxonomy_score, 1),
                "experience_alignment": round(exp_score, 1),
                "formatting_quality": round(format_score, 1),
                "quantification": round(quant_score, 1),
            },
        }

    def generate_priority_actions(self, score_result: Dict, gaps: Dict) -> List[Dict]:
        """Generate prioritized action items."""
        actions = []

        components = score_result.get("components", [])

        # Find weakest components
        sorted_components = sorted(components, key=lambda x: x["score"])

        for comp in sorted_components[:3]:  # Top 3 weakest areas
            if comp["score"] < 70:
                actions.append(
                    {
                        "area": comp["name"],
                        "score": comp["score"],
                        "priority": "high" if comp["score"] < 50 else "medium",
                        "action": self._get_action_for_component(
                            comp["name"], comp["score"]
                        ),
                    }
                )

        # Add gap-based actions
        for gap in gaps.get("high_priority", [])[:3]:
            actions.append(
                {"area": gap.type.title(), "priority": "high", "action": gap.suggestion}
            )

        return actions[:5]  # Top 5 actions

    def _get_action_for_component(self, name: str, score: float) -> str:
        """Get improvement action for a score component."""
        actions = {
            "Keyword Match": "Mirror exact keywords from the job description in your resume",
            "Semantic Match": "Reword your experience to align with the job requirements",
            "Skill Coverage": "Add missing required skills to your skills section",
            "Experience Alignment": "Tailor your experience bullets to match job responsibilities",
            "Formatting Quality": "Fix formatting issues and ensure ATS-friendly structure",
            "Quantification": "Add metrics and numbers to your achievement bullets",
        }
        return actions.get(name, "Improve this area of your resume")

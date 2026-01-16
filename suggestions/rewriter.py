"""
Generate specific rewrite suggestions for resume improvement.
"""

import re
from typing import List, Dict


class RewriteSuggester:
    """Generate actionable rewrite suggestions."""

    # Weak phrases to improve
    WEAK_PHRASES = {
        "responsible for": "Led",
        "helped with": "Contributed to",
        "worked on": "Developed",
        "was involved in": "Participated in",
        "assisted in": "Supported",
        "duties included": "Delivered",
        "in charge of": "Managed",
        "tasked with": "Executed",
    }

    # Action verb suggestions by category
    ACTION_VERBS = {
        "leadership": ["Led", "Directed", "Managed", "Orchestrated", "Spearheaded"],
        "creation": ["Developed", "Built", "Created", "Designed", "Engineered"],
        "improvement": ["Improved", "Enhanced", "Optimized", "Streamlined", "Revamped"],
        "achievement": [
            "Achieved",
            "Delivered",
            "Exceeded",
            "Surpassed",
            "Accomplished",
        ],
        "analysis": ["Analyzed", "Evaluated", "Assessed", "Investigated", "Researched"],
    }

    def __init__(self):
        pass

    def analyze_bullets(self, bullets: List[str]) -> List[Dict]:
        """Analyze experience bullets and suggest improvements."""
        suggestions = []

        for bullet in bullets:
            bullet_suggestions = []
            improved = bullet

            # Check for weak phrases
            for weak, strong in self.WEAK_PHRASES.items():
                if weak.lower() in bullet.lower():
                    improved = re.sub(weak, strong, improved, flags=re.IGNORECASE)
                    bullet_suggestions.append(
                        {
                            "type": "weak_phrase",
                            "original": weak,
                            "suggested": strong,
                            "reason": "Use stronger action verbs",
                        }
                    )

            # Check if starts with action verb
            first_word = bullet.split()[0] if bullet.split() else ""
            if not self._is_action_verb(first_word):
                bullet_suggestions.append(
                    {
                        "type": "no_action_verb",
                        "suggestion": f"Start with an action verb like: {', '.join(self.ACTION_VERBS['achievement'][:3])}",
                        "reason": "Bullets should start with strong action verbs",
                    }
                )

            # Check for quantification
            if not re.search(r"\d+%?|\$[\d,]+", bullet):
                bullet_suggestions.append(
                    {
                        "type": "no_metrics",
                        "suggestion": "Add specific numbers, percentages, or dollar amounts",
                        "reason": "Quantified achievements are more impactful",
                        "examples": [
                            "How many people/users were affected?",
                            "What percentage improvement?",
                            "What was the dollar impact?",
                            "How much time was saved?",
                        ],
                    }
                )

            # Check length
            if len(bullet) < 30:
                bullet_suggestions.append(
                    {
                        "type": "too_short",
                        "suggestion": "Add more details about impact and results",
                        "reason": "Bullet points should provide context and results",
                    }
                )
            elif len(bullet) > 200:
                bullet_suggestions.append(
                    {
                        "type": "too_long",
                        "suggestion": "Consider splitting into multiple bullets",
                        "reason": "Keep bullets concise and focused",
                    }
                )

            if bullet_suggestions:
                suggestions.append(
                    {
                        "original": bullet,
                        "improved": improved if improved != bullet else None,
                        "issues": bullet_suggestions,
                    }
                )

        return suggestions

    def _is_action_verb(self, word: str) -> bool:
        """Check if word is an action verb."""
        word_lower = word.lower().rstrip("ed").rstrip("ing")
        all_verbs = set()
        for verbs in self.ACTION_VERBS.values():
            all_verbs.update(v.lower() for v in verbs)
        return word_lower in all_verbs or word.lower().endswith("ed")

    def suggest_keyword_insertion(
        self, cv_text: str, missing_keywords: List[str]
    ) -> List[Dict]:
        """Suggest where to naturally add missing keywords."""
        suggestions = []

        for keyword in missing_keywords[:10]:  # Top 10 missing keywords
            suggestion = {"keyword": keyword, "insertion_points": []}

            # Suggest skills section
            suggestion["insertion_points"].append(
                {
                    "location": "Skills Section",
                    "how": f'Add "{keyword}" to your technical skills list',
                }
            )

            # Suggest experience section if technical skill
            if keyword.lower() in [
                "python",
                "java",
                "react",
                "aws",
                "docker",
                "kubernetes",
                "sql",
            ]:
                suggestion["insertion_points"].append(
                    {
                        "location": "Experience Section",
                        "how": f"Mention using {keyword} in a project or achievement",
                    }
                )

            suggestions.append(suggestion)

        return suggestions

    def generate_achievement_templates(self, role_type: str = "general") -> List[str]:
        """Generate achievement bullet templates."""
        templates = [
            "Developed [project/feature] using [technology], resulting in [quantified outcome]",
            "Led team of [number] to deliver [project] [percentage]% under budget/ahead of schedule",
            "Improved [process/metric] by [percentage]% through implementation of [solution]",
            "Managed [number] [projects/clients/accounts] generating [$amount] in revenue",
            "Reduced [metric] by [percentage]% by [action taken]",
            "Increased [metric] from [baseline] to [new value] over [timeframe]",
            "Automated [process] saving [number] hours per [week/month]",
            "Trained [number] team members on [skill/tool], improving team productivity by [percentage]%",
        ]

        return templates

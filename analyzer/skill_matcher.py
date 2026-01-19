"""
Skill taxonomy matching for intelligent skill recognition.
"""

import json
from pathlib import Path
from typing import Dict, Set, List, Tuple


class SkillMatcher:
    """Match skills using hierarchical taxonomy."""

    def __init__(self, taxonomy_path: str = None):
        if taxonomy_path is None:
            taxonomy_path = (
                Path(__file__).parent.parent / "config" / "skill_taxonomy.json"
            )

        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.skill_to_category = self._build_reverse_index()

    def _load_taxonomy(self, path: Path) -> Dict:
        """Load skill taxonomy from JSON."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _build_reverse_index(self) -> Dict[str, Tuple[str, str]]:
        """Build skill -> (category, parent) mapping."""
        index = {}

        for category, subcats in self.taxonomy.items():
            for subcat, skills in subcats.items():
                # Index the subcategory as a skill
                index[subcat.lower()] = (category, subcat)

                # Index all skills
                for skill in skills:
                    index[skill.lower()] = (category, subcat)

        return index

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills by taxonomy."""
        categorized = {}

        for skill in skills:
            skill_lower = skill.lower().strip()

            if skill_lower in self.skill_to_category:
                category, subcat = self.skill_to_category[skill_lower]
                key = f"{category}/{subcat}"
                if key not in categorized:
                    categorized[key] = []
                categorized[key].append(skill)
            else:
                # Check partial matches
                matched = False
                for indexed_skill, (category, subcat) in self.skill_to_category.items():
                    if indexed_skill in skill_lower or skill_lower in indexed_skill:
                        key = f"{category}/{subcat}"
                        if key not in categorized:
                            categorized[key] = []
                        categorized[key].append(skill)
                        matched = True
                        break

                if not matched:
                    if "uncategorized" not in categorized:
                        categorized["uncategorized"] = []
                    categorized["uncategorized"].append(skill)

        return categorized

    def find_related_skills(self, skill: str) -> List[str]:
        """Find related skills in the same subcategory."""
        skill_lower = skill.lower().strip()

        if skill_lower not in self.skill_to_category:
            return []

        category, subcat = self.skill_to_category[skill_lower]

        # Get all skills in the same subcategory
        if category in self.taxonomy and subcat in self.taxonomy[category]:
            related = self.taxonomy[category][subcat]
            return [s for s in related if s.lower() != skill_lower]

        return []

    def calculate_coverage(self, cv_skills: List[str], jd_skills: List[str]) -> Dict:
        """Calculate skill coverage with taxonomy awareness and fuzzy matching."""

        def normalize_skill(skill: str) -> str:
            """Normalize skill for comparison - handles variations."""
            s = skill.lower().strip()
            # Handle common variations
            s = s.replace("-", " ").replace("_", " ")
            s = s.replace(".js", "").replace("js", "")
            s = s.replace("'s", "s").replace("'", "")
            return s

        def skills_match(cv_skill: str, jd_skill: str) -> bool:
            """Check if two skills match with fuzzy logic."""
            cv_norm = normalize_skill(cv_skill)
            jd_norm = normalize_skill(jd_skill)

            # Exact match after normalization
            if cv_norm == jd_norm:
                return True

            # One contains the other
            if cv_norm in jd_norm or jd_norm in cv_norm:
                return True

            # Handle variations like "react native" vs "react-native"
            cv_words = set(cv_norm.split())
            jd_words = set(jd_norm.split())
            if cv_words == jd_words:
                return True

            return False

        cv_set = {s.lower().strip() for s in cv_skills}
        jd_set = {s.lower().strip() for s in jd_skills}

        # Direct matches (exact match after lowercasing)
        direct_matches = cv_set & jd_set

        # Fuzzy matches (similar but not exact)
        fuzzy_matches = set()
        for cv_skill in cv_set:
            for jd_skill in jd_set - direct_matches:
                if jd_skill not in direct_matches and skills_match(cv_skill, jd_skill):
                    fuzzy_matches.add(jd_skill)
                    direct_matches.add(jd_skill)  # Count as matched

        # Taxonomy-based matches (CV skill related to JD skill)
        taxonomy_matches = set()
        for cv_skill in cv_set:
            for jd_skill in jd_set:
                if cv_skill == jd_skill:
                    continue

                # Check if same subcategory
                cv_cat = self.skill_to_category.get(cv_skill)
                jd_cat = self.skill_to_category.get(jd_skill)

                if cv_cat and jd_cat and cv_cat == jd_cat:
                    taxonomy_matches.add((cv_skill, jd_skill))

        # Calculate coverage score
        if not jd_set:
            coverage_score = 0.0
        else:
            direct_coverage = len(direct_matches) / len(jd_set)
            # Taxonomy matches count for partial credit
            taxonomy_coverage = len(taxonomy_matches) * 0.5 / len(jd_set)
            coverage_score = min(1.0, direct_coverage + taxonomy_coverage)

        # Identify missing required skills
        missing_direct = jd_set - direct_matches
        # Filter out those covered by taxonomy matches
        covered_by_taxonomy = {jd for cv, jd in taxonomy_matches}
        missing_critical = missing_direct - covered_by_taxonomy

        return {
            "coverage_score": coverage_score,
            "direct_matches": list(direct_matches),
            "fuzzy_matches": list(fuzzy_matches),
            "taxonomy_matches": [(cv, jd) for cv, jd in taxonomy_matches],
            "missing_skills": list(missing_critical),
            "partially_covered": list(covered_by_taxonomy),
            "cv_categorized": self.categorize_skills(list(cv_set)),
            "jd_categorized": self.categorize_skills(list(jd_set)),
        }

    def get_skill_gaps_by_category(
        self, cv_skills: List[str], jd_skills: List[str]
    ) -> Dict[str, Dict]:
        """Get skill gaps organized by category."""
        cv_categorized = self.categorize_skills(cv_skills)
        jd_categorized = self.categorize_skills(jd_skills)

        gaps = {}

        all_categories = set(cv_categorized.keys()) | set(jd_categorized.keys())

        for category in all_categories:
            cv_in_cat = set(s.lower() for s in cv_categorized.get(category, []))
            jd_in_cat = set(s.lower() for s in jd_categorized.get(category, []))

            gaps[category] = {
                "cv_has": list(cv_in_cat),
                "jd_requires": list(jd_in_cat),
                "missing": list(jd_in_cat - cv_in_cat),
                "coverage": len(cv_in_cat & jd_in_cat) / len(jd_in_cat)
                if jd_in_cat
                else 1.0,
            }

        return gaps

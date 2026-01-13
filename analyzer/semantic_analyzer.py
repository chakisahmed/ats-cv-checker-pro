"""
Semantic analysis using sentence transformers.
"""

from typing import List, Dict, Tuple
import numpy as np

_model = None


def get_model():
    """Lazy load sentence transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


class SemanticAnalyzer:
    """Semantic similarity analysis using embeddings."""

    def __init__(self):
        self.model = None  # Lazy load

    def _get_model(self):
        if self.model is None:
            self.model = get_model()
        return self.model

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        model = self._get_model()
        embeddings = model.encode([text1, text2])

        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )

        return max(0.0, min(1.0, float(similarity)))

    def compute_section_similarities(
        self, cv_sections: Dict[str, str], jd_text: str
    ) -> Dict[str, float]:
        """Compute similarity for each CV section against JD."""
        model = self._get_model()
        section_scores = {}

        jd_embedding = model.encode([jd_text])[0]
        jd_norm = np.linalg.norm(jd_embedding)

        for section_name, section_text in cv_sections.items():
            if section_text and section_text.strip():
                section_embedding = model.encode([section_text])[0]
                section_norm = np.linalg.norm(section_embedding)

                if section_norm > 0 and jd_norm > 0:
                    similarity = np.dot(section_embedding, jd_embedding) / (
                        section_norm * jd_norm
                    )
                    section_scores[section_name] = max(0.0, min(1.0, float(similarity)))
                else:
                    section_scores[section_name] = 0.0
            else:
                section_scores[section_name] = 0.0

        return section_scores

    def find_similar_terms(
        self, cv_terms: List[str], jd_terms: List[str], threshold: float = 0.65
    ) -> List[Tuple[str, str, float]]:
        """Find semantically similar terms between CV and JD."""
        if not cv_terms or not jd_terms:
            return []

        model = self._get_model()

        cv_embeddings = model.encode(cv_terms)
        jd_embeddings = model.encode(jd_terms)

        similar_pairs = []

        for i, cv_emb in enumerate(cv_embeddings):
            cv_norm = np.linalg.norm(cv_emb)
            if cv_norm == 0:
                continue

            for j, jd_emb in enumerate(jd_embeddings):
                jd_norm = np.linalg.norm(jd_emb)
                if jd_norm == 0:
                    continue

                similarity = np.dot(cv_emb, jd_emb) / (cv_norm * jd_norm)

                if (
                    similarity >= threshold
                    and cv_terms[i].lower() != jd_terms[j].lower()
                ):
                    similar_pairs.append((cv_terms[i], jd_terms[j], float(similarity)))

        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        return similar_pairs[:25]

    def compute_experience_relevance(
        self, experience_bullets: List[str], jd_text: str
    ) -> List[Dict]:
        """Score each experience bullet for relevance to JD."""
        if not experience_bullets:
            return []

        model = self._get_model()

        jd_embedding = model.encode([jd_text])[0]
        jd_norm = np.linalg.norm(jd_embedding)

        results = []
        for bullet in experience_bullets:
            if bullet.strip():
                bullet_emb = model.encode([bullet])[0]
                bullet_norm = np.linalg.norm(bullet_emb)

                if bullet_norm > 0 and jd_norm > 0:
                    score = np.dot(bullet_emb, jd_embedding) / (bullet_norm * jd_norm)
                else:
                    score = 0.0

                results.append(
                    {"text": bullet, "relevance": max(0.0, min(1.0, float(score)))}
                )

        return sorted(results, key=lambda x: x["relevance"], reverse=True)

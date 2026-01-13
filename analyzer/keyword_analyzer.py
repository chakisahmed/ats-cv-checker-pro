"""
Enhanced keyword analysis with tech-aware extraction.
"""
import re
from collections import Counter
from typing import Set, Dict, List, Tuple

import spacy

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


# Extended tech keywords
TECH_KEYWORDS = {
    'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
    'node', 'nodejs', 'django', 'flask', 'fastapi', 'spring', 'sql', 'nosql',
    'mongodb', 'postgresql', 'mysql', 'redis', 'docker', 'kubernetes', 'aws',
    'azure', 'gcp', 'git', 'ci/cd', 'jenkins', 'terraform', 'ansible',
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
    'pytorch', 'pandas', 'numpy', 'scikit-learn', 'data analysis', 'data science',
    'agile', 'scrum', 'jira', 'confluence', 'rest', 'api', 'microservices',
    'html', 'css', 'sass', 'webpack', 'graphql', 'linux', 'unix', 'bash',
    'c++', 'c#', 'rust', 'go', 'golang', 'scala', 'kotlin', 'swift',
    'excel', 'powerbi', 'tableau', 'spark', 'hadoop', 'kafka', 'elasticsearch',
    'devops', 'cicd', 'cloud', 'serverless', 'lambda', 'ec2', 's3'
}

ACTION_VERBS = {
    'managed', 'developed', 'designed', 'implemented', 'created', 'built',
    'led', 'coordinated', 'analyzed', 'optimized', 'improved', 'delivered',
    'architected', 'deployed', 'maintained', 'collaborated', 'mentored',
    'automated', 'integrated', 'tested', 'debugged', 'resolved', 'achieved',
    'increased', 'reduced', 'streamlined', 'launched', 'executed', 'established',
    'spearheaded', 'pioneered', 'orchestrated', 'transformed', 'revamped'
}

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what',
    'which', 'who', 'where', 'when', 'why', 'how', 'all', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just'
}


class KeywordAnalyzer:
    """Enhanced keyword extraction and analysis."""
    
    def __init__(self):
        self.nlp = get_nlp()
    
    def extract_keywords(self, text: str, top_n: int = 50) -> Dict:
        """Extract keywords with categorization."""
        if not text or not text.strip():
            return self._empty_result()
        
        doc = self.nlp(text.lower())
        
        skills = []
        action_verbs = []
        noun_phrases = []
        all_keywords = []
        
        # Process tokens
        for token in doc:
            word = token.text.strip()
            lemma = token.lemma_.strip()
            
            if len(word) < 2 or word in STOPWORDS:
                continue
            
            if word in TECH_KEYWORDS or lemma in TECH_KEYWORDS:
                skills.append(word)
                all_keywords.append(word)
            elif token.pos_ == 'VERB' and (word in ACTION_VERBS or lemma in ACTION_VERBS):
                action_verbs.append(lemma)
                all_keywords.append(lemma)
            elif token.pos_ in ('NOUN', 'PROPN') and not token.is_stop:
                all_keywords.append(lemma)
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip()
            if len(phrase.split()) >= 2 and phrase.lower() not in STOPWORDS:
                if any(kw in phrase.lower() for kw in TECH_KEYWORDS):
                    skills.append(phrase)
                noun_phrases.append(phrase)
                all_keywords.append(phrase)
        
        return {
            'all_keywords': Counter(all_keywords).most_common(top_n),
            'skills': Counter(skills).most_common(30),
            'action_verbs': Counter(action_verbs).most_common(20),
            'noun_phrases': Counter(noun_phrases).most_common(25),
        }
    
    def get_keyword_set(self, text: str) -> Set[str]:
        """Get normalized keyword set."""
        keywords = self.extract_keywords(text)
        result = set()
        
        for kw, _ in keywords['all_keywords']:
            result.add(kw.lower().strip())
        for kw, _ in keywords['skills']:
            result.add(kw.lower().strip())
        
        return result
    
    def calculate_match(self, cv_keywords: Set[str], jd_keywords: Set[str]) -> Dict:
        """Calculate keyword match statistics."""
        if not jd_keywords:
            return {'score': 0, 'matching': set(), 'missing': set()}
        
        matching = cv_keywords & jd_keywords
        missing = jd_keywords - cv_keywords
        score = len(matching) / len(jd_keywords)
        
        return {
            'score': min(1.0, score),
            'matching': matching,
            'missing': missing,
            'cv_only': cv_keywords - jd_keywords
        }
    
    def _empty_result(self) -> Dict:
        return {
            'all_keywords': [],
            'skills': [],
            'action_verbs': [],
            'noun_phrases': [],
        }

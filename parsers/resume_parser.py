"""
Advanced resume parser using spaCy NER and pattern matching.
Extracts structured data from CV text.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

import spacy

# Lazy load spaCy
_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            import sys

            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
            )
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


@dataclass
class ContactInfo:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Experience:
    company: str = ""
    title: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str = ""
    bullets: List[str] = field(default_factory=list)
    is_current: bool = False


@dataclass
class Education:
    institution: str = ""
    degree: str = ""
    field: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None


@dataclass
class ParsedResume:
    contact: ContactInfo = field(default_factory=ContactInfo)
    summary: str = ""
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    projects: List[Dict] = field(default_factory=list)
    raw_text: str = ""
    sections: Dict[str, str] = field(default_factory=dict)


class ResumeParser:
    """Advanced resume parser with ML-based entity extraction."""

    # Section header patterns
    SECTION_PATTERNS = {
        "summary": r"(?:summary|profile|objective|about\s*me|professional\s*summary)",
        "experience": r"(?:experience|work\s*history|employment|professional\s*experience|work\s*experience)",
        "education": r"(?:education|academic|qualifications|degrees)",
        "skills": r"(?:skills|technical\s*skills|competencies|technologies|expertise)",
        "certifications": r"(?:certifications?|licenses?|credentials|certificates)",
        "projects": r"(?:projects|portfolio|personal\s*projects)",
    }

    # Date patterns
    DATE_PATTERN = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[,.\s]*\d{4}|\d{1,2}/\d{4}|\d{4}"
    DATE_RANGE_PATTERN = (
        rf"({DATE_PATTERN})\s*[-–—to]+\s*({DATE_PATTERN}|present|current|now)"
    )

    def __init__(self):
        self.nlp = get_nlp()

    def parse(self, text: str) -> ParsedResume:
        """Parse resume text into structured data."""
        resume = ParsedResume(raw_text=text)

        # Extract sections first
        resume.sections = self._extract_sections(text)

        # Extract contact info
        resume.contact = self._extract_contact(text)

        # Extract summary
        resume.summary = resume.sections.get("summary", "")

        # Extract skills
        resume.skills = self._extract_skills(text, resume.sections.get("skills", ""))

        # Extract experience
        resume.experiences = self._extract_experiences(
            resume.sections.get("experience", "")
        )

        # Extract education
        resume.education = self._extract_education(resume.sections.get("education", ""))

        # Extract certifications
        resume.certifications = self._extract_certifications(
            resume.sections.get("certifications", "")
        )

        # Extract projects
        resume.projects = self._extract_projects(resume.sections.get("projects", ""))

        return resume

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract text content for each section."""
        sections = {}
        text_lower = text.lower()

        # Find all section positions
        section_positions = []
        for section_name, pattern in self.SECTION_PATTERNS.items():
            for match in re.finditer(pattern, text_lower):
                section_positions.append((match.start(), match.end(), section_name))

        # Sort by position
        section_positions.sort(key=lambda x: x[0])

        # Extract content between sections
        for i, (start, header_end, section_name) in enumerate(section_positions):
            end = (
                section_positions[i + 1][0]
                if i + 1 < len(section_positions)
                else len(text)
            )
            content = text[header_end:end].strip()

            # Remove the section header from content
            lines = content.split("\n")
            if lines:
                content = "\n".join(lines).strip()

            if section_name not in sections or len(content) > len(
                sections.get(section_name, "")
            ):
                sections[section_name] = content

        return sections

    def _extract_contact(self, text: str) -> ContactInfo:
        """Extract contact information using patterns and NER."""
        contact = ContactInfo()

        # Email pattern
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        if email_match:
            contact.email = email_match.group()

        # Phone pattern (various formats)
        phone_match = re.search(
            r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text
        )
        if phone_match:
            contact.phone = phone_match.group()

        # LinkedIn pattern
        linkedin_match = re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()

        # Name - try to get from first lines or NER
        doc = self.nlp(text[:500])  # First 500 chars for name
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                contact.name = ent.text
                break

        # Location from NER
        for ent in doc.ents:
            if ent.label_ == "GPE":
                contact.location = ent.text
                break

        return contact

    def _extract_skills(self, full_text: str, skills_section: str) -> List[str]:
        """Extract skills from skills section and throughout the document."""
        skills = set()

        # Process skills section specifically
        if skills_section:
            # Split by common delimiters
            skill_candidates = re.split(r"[,|•·\n\r]+", skills_section)
            for skill in skill_candidates:
                skill = skill.strip()
                if skill and len(skill) > 1 and len(skill) < 50:
                    # Remove bullet points and special chars at start
                    skill = re.sub(r"^[-*•·]\s*", "", skill)
                    if skill:
                        skills.add(skill)

        # Also extract using NER from full text
        doc = self.nlp(full_text)
        for ent in doc.ents:
            if ent.label_ in ("PRODUCT", "ORG"):
                # Filter for likely tech skills
                if len(ent.text) > 1 and len(ent.text) < 30:
                    skills.add(ent.text)

        return list(skills)

    def _extract_experiences(self, experience_text: str) -> List[Experience]:
        """Extract work experiences with dates and descriptions."""
        experiences = []

        if not experience_text:
            return experiences

        # Split by date ranges (likely new job entries)
        date_range_matches = list(
            re.finditer(self.DATE_RANGE_PATTERN, experience_text, re.IGNORECASE)
        )

        if date_range_matches:
            for i, match in enumerate(date_range_matches):
                exp = Experience()
                exp.start_date = match.group(1)
                exp.end_date = match.group(2)
                exp.is_current = (
                    "present" in match.group(2).lower()
                    or "current" in match.group(2).lower()
                )

                # Get text before this date (likely company/title)
                start_pos = date_range_matches[i - 1].end() if i > 0 else 0
                pre_text = experience_text[start_pos : match.start()].strip()

                # Get text after date until next entry
                end_pos = (
                    date_range_matches[i + 1].start()
                    if i + 1 < len(date_range_matches)
                    else len(experience_text)
                )
                post_text = experience_text[match.end() : end_pos].strip()

                # Extract title and company from pre_text
                lines = [l.strip() for l in pre_text.split("\n") if l.strip()]
                if len(lines) >= 2:
                    line_a = lines[-1]  # Bottom line
                    line_b = lines[-2]  # Top line

                    # Check if the bottom line is a Company
                    doc_a = self.nlp(line_a)
                    if any(ent.label_ == "ORG" for ent in doc_a.ents):
                        exp.company = line_a
                        exp.title = line_b
                    else:
                        # Check if top line is an ORG
                        doc_b = self.nlp(line_b)
                        if any(ent.label_ == "ORG" for ent in doc_b.ents):
                            exp.company = line_b
                            exp.title = line_a
                        else:
                            # Default: assume first line is title, second is company
                            exp.title = line_b
                            exp.company = line_a
                elif len(lines) == 1:
                    # Single line - try to determine if it's company or title
                    doc = self.nlp(lines[0])
                    if any(ent.label_ == "ORG" for ent in doc.ents):
                        exp.company = lines[0]
                    else:
                        exp.title = lines[0]

                # Extract bullets from post_text
                bullets = re.findall(r"[•\-\*]\s*(.+)", post_text)
                exp.bullets = bullets
                exp.description = post_text

                experiences.append(exp)

        return experiences

    def _extract_education(self, education_text: str) -> List[Education]:
        """Extract education entries."""
        education = []

        if not education_text:
            return education

        # Common degree patterns
        degree_patterns = [
            r"(Bachelor'?s?|Master'?s?|PhD|Ph\.D|MBA|B\.S\.?|M\.S\.?|B\.A\.?|M\.A\.?|Associate'?s?)\s+(?:of\s+)?(?:Science|Arts|Engineering|Business|Administration)?",
            r"(B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|Ph\.?D\.?|MBA)\s+(?:in\s+)?(\w+(?:\s+\w+)?)",
        ]

        # Find degree mentions
        for pattern in degree_patterns:
            matches = re.finditer(pattern, education_text, re.IGNORECASE)
            for match in matches:
                edu = Education()
                edu.degree = match.group(0)
                education.append(edu)

        # Fallback: Use spaCy to find institutions (ORG entities)
        if not education and education_text:
            doc = self.nlp(education_text)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    edu = Education()
                    edu.institution = ent.text
                    # Try to extract surrounding text for field of study
                    start = max(0, ent.start_char - 50)
                    end = min(len(education_text), ent.end_char + 100)
                    context = education_text[start:end]
                    edu.degree = context.strip()[:200]
                    education.append(edu)
                    break  # Take first institution found

        # Ultimate fallback: just capture the raw text
        if not education and education_text:
            edu = Education()
            edu.degree = education_text[:200]  # Truncate
            education.append(edu)

        return education

    def _extract_certifications(self, cert_text: str) -> List[str]:
        """Extract certifications."""
        if not cert_text:
            return []

        # Split by lines or bullets
        certs = re.split(r"[\n•\-*]+", cert_text)
        return [c.strip() for c in certs if c.strip() and len(c.strip()) > 3]

    def _extract_projects(self, project_text: str) -> List[Dict]:
        """Extract projects with descriptions."""
        projects = []

        if not project_text:
            return projects

        # Regex to detect date-only lines
        DATE_ONLY_PATTERN = r"^(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[\s,]*\d{4}(?:\s*[-–—]\s*(?:Present|Current|Now|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*\d{4}))?$"

        # Simple split by double newlines or bullets
        entries = re.split(r"\n\n+", project_text)
        for entry in entries:
            if entry.strip():
                lines = entry.strip().split("\n")
                project_name = lines[0].strip()[:100]

                # Skip date-only first lines
                if re.match(DATE_ONLY_PATTERN, project_name, re.IGNORECASE):
                    project_name = (
                        lines[1].strip()[:100] if len(lines) > 1 else "Unnamed Project"
                    )

                projects.append(
                    {
                        "name": project_name,
                        "description": entry.strip(),
                    }
                )

        return projects[:10]  # Limit to 10 projects

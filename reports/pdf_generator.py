"""
PDF report generator using fpdf2.
"""

from fpdf import FPDF
from typing import Dict, List
from datetime import datetime
import io


class ATSReportPDF(FPDF):
    """Custom PDF class for ATS reports."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, "ATS CV Checker Pro - Analysis Report", ln=True, align="C")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(128, 128, 128)
        self.cell(
            0,
            6,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ln=True,
            align="C",
        )
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(31, 41, 55)
        self.cell(0, 10, title, ln=True)
        self.set_draw_color(102, 126, 234)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def add_score_box(self, score: float, label: str):
        # Color based on score
        if score >= 80:
            r, g, b = 16, 185, 129
        elif score >= 60:
            r, g, b = 59, 130, 246
        elif score >= 40:
            r, g, b = 245, 158, 11
        else:
            r, g, b = 239, 68, 68

        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 24)

        x = self.get_x()
        y = self.get_y()

        # Draw box
        self.rect(x, y, 50, 25, "F")
        self.set_xy(x, y + 7)
        self.cell(50, 10, f"{score:.0f}%", align="C")

        # Label
        self.set_xy(x + 55, y + 7)
        self.set_text_color(31, 41, 55)
        self.set_font("Helvetica", "", 12)
        self.cell(0, 10, label)

        self.set_y(y + 30)

    def add_bullet_list(self, items: List[str], indent: int = 10):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(55, 65, 81)

        for item in items:
            self.set_x(indent)
            self.multi_cell(0, 6, f"- {item}")


def generate_pdf_report(
    score_result: Dict,
    skill_coverage: Dict,
    gaps: Dict,
    recommendations: List[str],
    parsed_resume=None,
) -> bytes:
    """Generate PDF report from analysis results."""

    pdf = ATSReportPDF()
    pdf.add_page()

    # Overall Score Section
    pdf.section_title("Overall ATS Score")
    pdf.add_score_box(
        score_result["overall_score"],
        f"Grade: {score_result['grade']} - {score_result['grade_label']}",
    )
    pdf.ln(5)

    # Score Components
    pdf.section_title("Score Breakdown")
    pdf.set_font("Helvetica", "", 10)

    for comp in score_result.get("components", []):
        score = comp["score"]
        if score >= 70:
            status = "[OK]"
        else:
            status = "[X]"

        pdf.set_text_color(55, 65, 81)
        pdf.cell(80, 7, f"{comp['name']}", ln=False)
        pdf.cell(30, 7, f"{score:.0f}%", ln=False)
        pdf.cell(40, 7, f"({comp['weight'] * 100:.0f}% weight)", ln=False)
        pdf.cell(0, 7, comp["details"], ln=True)

    pdf.ln(5)

    # Skills Analysis
    pdf.section_title("Skills Analysis")

    direct_matches = skill_coverage.get("direct_matches", [])
    missing = skill_coverage.get("missing_skills", [])

    if direct_matches:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(16, 185, 129)
        pdf.cell(0, 8, f"Matching Skills ({len(direct_matches)})", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(55, 65, 81)
        pdf.multi_cell(0, 6, ", ".join(direct_matches[:15]))
        pdf.ln(3)

    if missing:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 8, f"Missing Skills ({len(missing)})", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(55, 65, 81)
        pdf.multi_cell(0, 6, ", ".join(missing[:15]))
        pdf.ln(3)

    # Priority Actions
    pdf.section_title("Priority Actions")

    high_priority = gaps.get("high_priority", [])
    if high_priority:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 8, "High Priority Issues:", ln=True)

        for gap in high_priority[:5]:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(55, 65, 81)
            pdf.set_x(15)
            pdf.multi_cell(0, 6, f"- {gap.description}")
            pdf.set_x(20)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(107, 114, 128)
            pdf.multi_cell(0, 5, f"  -> {gap.suggestion}")
            pdf.ln(2)

    # Recommendations
    if recommendations:
        pdf.add_page()
        pdf.section_title("Recommendations")
        pdf.add_bullet_list(recommendations[:10])

    # Return PDF as bytes
    return bytes(pdf.output())

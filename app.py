"""
ATS CV Checker Pro - Advanced Streamlit Application
Comprehensive CV analysis with ML-powered insights.
"""

import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="ATS CV Checker Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

from parsers import parse_document, ResumeParser
from analyzer import (
    KeywordAnalyzer,
    SemanticAnalyzer,
    SkillMatcher,
    GapAnalyzer,
    AdvancedScorer,
)
from suggestions import RewriteSuggester, ATSOptimizer
from reports import generate_pdf_report
from ui import render_score_card, render_skill_tags, render_recommendation
from ui.charts import (
    create_radar_chart,
    create_skill_heatmap,
    create_score_breakdown,
    create_experience_relevance_chart,
)


# Initialize session state for analysis results
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "results" not in st.session_state:
    st.session_state.results = {}


# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .pro-badge {
        display: inline-block;
        background: #ffd700;
        color: #333;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""",
    unsafe_allow_html=True,
)


def run_analysis(uploaded_file, job_description):
    """Run the analysis and store results in session state."""
    try:
        # Create progress bar
        progress = st.progress(0, text="📄 Parsing resume...")

        # Parse CV
        cv_text = parse_document(uploaded_file, uploaded_file.name)

        if not cv_text.strip():
            return False, "Could not extract text from CV"

        progress.progress(10, text="⚙️ Initializing analyzers...")

        # Initialize analyzers
        resume_parser = ResumeParser()
        keyword_analyzer = KeywordAnalyzer()
        semantic_analyzer = SemanticAnalyzer()
        skill_matcher = SkillMatcher()
        gap_analyzer = GapAnalyzer()
        scorer = AdvancedScorer()
        rewriter = RewriteSuggester()
        optimizer = ATSOptimizer()

        progress.progress(20, text="📋 Extracting resume structure...")

        # Parse resume structure
        parsed_resume = resume_parser.parse(cv_text)

        progress.progress(30, text="🔑 Analyzing keywords...")

        # Extract keywords
        cv_keywords = keyword_analyzer.get_keyword_set(cv_text)
        jd_keywords = keyword_analyzer.get_keyword_set(job_description)
        keyword_result = keyword_analyzer.calculate_match(cv_keywords, jd_keywords)

        progress.progress(45, text="🧠 Running semantic analysis...")

        # Semantic analysis
        semantic_score = semantic_analyzer.compute_similarity(cv_text, job_description)
        section_similarities = semantic_analyzer.compute_section_similarities(
            parsed_resume.sections, job_description
        )

        progress.progress(60, text="💼 Evaluating experience relevance...")

        # Get all experience bullets
        all_bullets = []
        for exp in parsed_resume.experiences:
            all_bullets.extend(exp.bullets)

        experience_relevance = semantic_analyzer.compute_experience_relevance(
            all_bullets, job_description
        )

        progress.progress(70, text="🎯 Matching skills...")

        # Skill matching
        cv_skills = list(keyword_analyzer.extract_keywords(cv_text)["skills"])
        cv_skill_names = [s[0] for s in cv_skills]
        jd_skills = list(keyword_analyzer.extract_keywords(job_description)["skills"])
        jd_skill_names = [s[0] for s in jd_skills]

        skill_coverage = skill_matcher.calculate_coverage(
            cv_skill_names, jd_skill_names
        )
        skill_gaps = skill_matcher.get_skill_gaps_by_category(
            cv_skill_names, jd_skill_names
        )

        progress.progress(80, text="🔍 Analyzing gaps...")

        # Gap analysis
        gaps = gap_analyzer.analyze(parsed_resume, jd_skill_names, cv_skill_names)

        progress.progress(90, text="📊 Calculating scores...")

        # Calculate scores
        score_result = scorer.calculate_score(
            keyword_result,
            semantic_score,
            skill_coverage,
            experience_relevance,
            gaps,
            parsed_resume,
        )

        # Get priority actions
        priority_actions = scorer.generate_priority_actions(score_result, gaps)

        # ATS optimization
        ats_result = optimizer.score_ats_friendliness(parsed_resume, gaps)

        # Bullet suggestions
        bullet_suggestions = rewriter.analyze_bullets(all_bullets[:10])

        progress.progress(100, text="✅ Analysis complete!")

        # Store all results in session state
        st.session_state.results = {
            "score_result": score_result,
            "skill_coverage": skill_coverage,
            "skill_gaps": skill_gaps,
            "gaps": gaps,
            "priority_actions": priority_actions,
            "ats_result": ats_result,
            "bullet_suggestions": bullet_suggestions,
            "parsed_resume": parsed_resume,
            "rewriter": rewriter,
            "optimizer": optimizer,
        }
        st.session_state.analysis_done = True

        return True, None

    except Exception as e:
        return False, str(e)


def display_results():
    """Display analysis results from session state."""
    results = st.session_state.results

    score_result = results["score_result"]
    skill_coverage = results["skill_coverage"]
    skill_gaps = results["skill_gaps"]
    gaps = results["gaps"]
    priority_actions = results["priority_actions"]
    ats_result = results["ats_result"]
    bullet_suggestions = results["bullet_suggestions"]
    parsed_resume = results["parsed_resume"]
    rewriter = results["rewriter"]
    optimizer = results["optimizer"]

    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    # Score overview
    score_cols = st.columns([1, 2])

    with score_cols[0]:
        render_score_card(score_result["overall_score"], "Overall ATS Score")
        st.markdown("<br>", unsafe_allow_html=True)

        # Grade badge
        grade = score_result["grade"]
        label = score_result["grade_label"]
        grade_colors = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"}
        st.markdown(f"### {grade_colors.get(grade, '⚪')} Grade: **{grade}** - {label}")

    with score_cols[1]:
        # Radar chart
        radar_data = score_result["breakdown"]
        radar_fig = create_radar_chart(radar_data, "Score Components")
        st.plotly_chart(radar_fig, use_container_width=True)

    # Score component breakdown
    st.markdown("### 📈 Score Breakdown")
    breakdown_fig = create_score_breakdown(score_result["components"])
    st.plotly_chart(breakdown_fig, use_container_width=True)

    # Tabs for detailed analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🔑 Skills", "⚡ Gaps", "✍️ Improvements", "📋 ATS Check", "📄 Export"]
    )

    with tab1:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### ✅ Matching Skills")
            if skill_coverage.get("direct_matches"):
                render_skill_tags(skill_coverage["direct_matches"], "match")
            else:
                st.info("No direct skill matches found")

        with col_b:
            st.markdown("#### ❌ Missing Skills")
            if skill_coverage.get("missing_skills"):
                render_skill_tags(skill_coverage["missing_skills"], "missing")
            else:
                st.success("No critical skills missing!")

        # Skill heatmap
        if skill_gaps:
            st.markdown("#### 📊 Skill Coverage by Category")
            heatmap = create_skill_heatmap(skill_gaps)
            if heatmap:
                st.plotly_chart(heatmap, use_container_width=True)

        # Related skills
        if skill_coverage.get("taxonomy_matches"):
            st.markdown("#### 🔗 Related Skills (Partial Match)")
            for cv_skill, jd_skill in skill_coverage["taxonomy_matches"][:5]:
                st.markdown(
                    f"- Your skill **{cv_skill}** is related to required **{jd_skill}**"
                )

    with tab2:
        st.markdown("#### 🔍 Identified Issues")

        if gaps["high_priority"]:
            st.markdown("##### 🔴 High Priority")
            for gap in gaps["high_priority"]:
                with st.expander(f"**{gap.type.title()}**: {gap.description}"):
                    st.write(f"**Suggestion:** {gap.suggestion}")

        if gaps["medium_priority"]:
            st.markdown("##### 🟡 Medium Priority")
            for gap in gaps["medium_priority"]:
                with st.expander(f"**{gap.type.title()}**: {gap.description}"):
                    st.write(f"**Suggestion:** {gap.suggestion}")

        if gaps["low_priority"]:
            st.markdown("##### 🟢 Low Priority")
            for gap in gaps["low_priority"][:3]:
                with st.expander(f"**{gap.type.title()}**: {gap.description}"):
                    st.write(f"**Suggestion:** {gap.suggestion}")

        if not gaps["gaps"]:
            st.success("No significant gaps detected!")

    with tab3:
        st.markdown("#### ✏️ Bullet Point Improvements")

        if bullet_suggestions:
            for i, suggestion in enumerate(bullet_suggestions[:5]):
                with st.expander(f"Bullet {i + 1}: {suggestion['original'][:60]}..."):
                    st.markdown("**Original:**")
                    st.text(suggestion["original"])

                    if suggestion["improved"]:
                        st.markdown("**Suggested:**")
                        st.text(suggestion["improved"])

                    st.markdown("**Issues:**")
                    for issue in suggestion["issues"]:
                        st.markdown(
                            f"- {issue.get('suggestion', issue.get('reason', ''))}"
                        )
        else:
            st.info("No experience bullets found to analyze")

        # Achievement templates
        st.markdown("#### 📝 Achievement Templates")
        templates = rewriter.generate_achievement_templates()
        for template in templates[:4]:
            st.code(template, language=None)

    with tab4:
        st.markdown("#### 🤖 ATS Compatibility")

        ats_score = ats_result["ats_score"]
        render_score_card(ats_score, "ATS Friendliness Score", size="small")

        st.markdown(f"**Assessment:** {ats_result['recommendation']}")

        if ats_result["issues"]:
            st.markdown("**Issues Found:**")
            for issue in ats_result["issues"]:
                st.markdown(f"- ❌ {issue}")

        st.markdown("#### ✅ Pre-Submission Checklist")
        checklist = optimizer.generate_checklist()
        for item in checklist:
            icon = "🔴" if item["critical"] else "🟡"
            st.checkbox(f"{icon} {item['item']}", key=f"check_{item['item'][:20]}")

    with tab5:
        st.markdown("#### 📄 Export Analysis Report")

        st.info("Generate a professional PDF report of your analysis")

        # Generate recommendations list
        recommendations = [action["action"] for action in priority_actions]
        recommendations.extend([g.suggestion for g in gaps["high_priority"][:3]])

        # Generate PDF immediately and show download button
        pdf_bytes = generate_pdf_report(
            score_result,
            skill_coverage,
            gaps,
            recommendations,
            parsed_resume,
        )

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name="ats_analysis_report.pdf",
            mime="application/pdf",
            type="primary",
        )

    # Priority Actions Summary
    st.markdown("---")
    st.markdown("### 🎯 Top Priority Actions")

    action_cols = st.columns(min(len(priority_actions), 3) if priority_actions else 1)

    if priority_actions:
        for i, action in enumerate(priority_actions[:3]):
            with action_cols[i]:
                priority = action.get("priority", "medium")
                render_recommendation(action["action"], priority)
    else:
        st.success("Your resume is well-optimized! No major actions needed.")


def main():
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🎯 ATS CV Checker <span class="pro-badge">PRO</span></h1>
        <p>Advanced AI-powered resume analysis with industry insights</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Pro Features")
        st.markdown("""
        - **6-Component Scoring** - Detailed breakdown
        - **Skill Taxonomy** - Related skill matching
        - **Gap Analysis** - Employment & skill gaps
        - **Rewrite Suggestions** - Improve your bullets
        - **PDF Export** - Professional reports
        - **Interactive Charts** - Visual analytics
        """)

        st.markdown("---")
        st.markdown("### 📊 Score Weights")
        st.markdown("""
        | Component | Weight |
        |-----------|--------|
        | Keywords | 20% |
        | Semantic | 20% |
        | Skills | 20% |
        | Experience | 15% |
        | Formatting | 15% |
        | Metrics | 10% |
        """)

        # Clear results button
        if st.session_state.analysis_done:
            st.markdown("---")
            if st.button("🔄 New Analysis", use_container_width=True):
                st.session_state.analysis_done = False
                st.session_state.results = {}
                st.rerun()

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📎 Upload Your CV")
        uploaded_file = st.file_uploader(
            "Drag and drop or browse",
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, DOCX, TXT",
        )
        if uploaded_file:
            st.success(f"✅ Loaded: {uploaded_file.name}")

    with col2:
        st.markdown("### 📋 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Copy and paste the full job description...",
        )

    st.markdown("---")

    analyze_btn = st.button(
        "🔍 Analyze CV",
        type="primary",
        use_container_width=True,
        disabled=not (uploaded_file and job_description),
    )

    if not uploaded_file:
        st.info("👆 Please upload your CV to begin")
    elif not job_description:
        st.info("👆 Please paste a job description")

    # Run analysis if button clicked
    if analyze_btn and uploaded_file and job_description:
        with st.spinner(
            "🔄 Performing advanced analysis... (first run may take longer to load models)"
        ):
            success, error = run_analysis(uploaded_file, job_description)
            if not success:
                st.error(f"❌ Error during analysis: {error}")
                st.info(
                    "If this is your first run, models may need to download. Please try again."
                )

    # Display results if analysis is done
    if st.session_state.analysis_done:
        display_results()


if __name__ == "__main__":
    main()

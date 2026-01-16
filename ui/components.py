"""
Reusable UI components for Streamlit.
"""

import streamlit as st


def render_score_card(score: float, label: str, size: str = "large"):
    """Render a score card with color coding."""
    if score >= 80:
        color = "#10b981"  # Green
        bg = "#d1fae5"
    elif score >= 60:
        color = "#3b82f6"  # Blue
        bg = "#dbeafe"
    elif score >= 40:
        color = "#f59e0b"  # Orange
        bg = "#fef3c7"
    else:
        color = "#ef4444"  # Red
        bg = "#fee2e2"

    font_size = "3rem" if size == "large" else "1.5rem"

    st.markdown(
        f"""
    <div style="
        background: linear-gradient(135deg, {bg} 0%, white 100%);
        border-left: 5px solid {color};
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">{label}</div>
        <div style="font-size: {font_size}; font-weight: bold; color: {color};">{score:.0f}%</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_skill_tags(skills: list, tag_type: str = "match"):
    """Render skill tags with appropriate styling."""
    if tag_type == "match":
        bg_color = "#d1fae5"
        text_color = "#065f46"
    elif tag_type == "missing":
        bg_color = "#fee2e2"
        text_color = "#991b1b"
    elif tag_type == "partial":
        bg_color = "#fef3c7"
        text_color = "#92400e"
    else:
        bg_color = "#e5e7eb"
        text_color = "#374151"

    tags_html = ""
    for skill in skills[:20]:  # Limit to 20
        tags_html += f"""
        <span style="
            display: inline-block;
            padding: 0.25rem 0.75rem;
            margin: 0.25rem;
            border-radius: 20px;
            font-size: 0.85rem;
            background-color: {bg_color};
            color: {text_color};
        ">{skill}</span>
        """

    st.markdown(tags_html, unsafe_allow_html=True)


def render_recommendation(text: str, priority: str = "medium"):
    """Render a recommendation card."""
    if priority == "high":
        border_color = "#ef4444"
        icon = "🔴"
    elif priority == "medium":
        border_color = "#f59e0b"
        icon = "🟡"
    else:
        border_color = "#10b981"
        icon = "🟢"

    st.markdown(
        f"""
    <div style="
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid {border_color};
    ">
        {icon} {text}
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_grade_badge(grade: str, label: str):
    """Render a letter grade badge."""
    colors = {
        "A": ("#10b981", "#d1fae5"),
        "B": ("#3b82f6", "#dbeafe"),
        "C": ("#f59e0b", "#fef3c7"),
        "D": ("#ef4444", "#fee2e2"),
        "F": ("#991b1b", "#fee2e2"),
    }

    color, bg = colors.get(grade, ("#6b7280", "#e5e7eb"))

    st.markdown(
        f"""
    <div style="
        display: inline-block;
        background: {bg};
        border: 3px solid {color};
        border-radius: 50%;
        width: 80px;
        height: 80px;
        line-height: 74px;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        color: {color};
    ">{grade}</div>
    <div style="text-align: center; margin-top: 0.5rem; color: {color}; font-weight: 600;">{label}</div>
    """,
        unsafe_allow_html=True,
    )


def render_component_bar(name: str, score: float, weight: float):
    """Render a score component with progress bar."""
    weighted = score * weight

    st.markdown(f"**{name}** ({weight * 100:.0f}% weight)")
    st.progress(score / 100)
    st.caption(f"{score:.0f}% → contributes {weighted:.1f} points")


def render_gap_item(gap, expanded: bool = False):
    """Render a gap/issue item."""
    severity_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}

    icon = severity_icons.get(gap.severity, "⚪")

    with st.expander(
        f"{icon} **{gap.type.title()}**: {gap.description}", expanded=expanded
    ):
        st.write(f"**Suggestion:** {gap.suggestion}")

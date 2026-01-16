"""
Interactive charts using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List


def create_radar_chart(
    scores: Dict[str, float], title: str = "Score Breakdown"
) -> go.Figure:
    """Create a radar chart for multi-dimensional score breakdown."""
    categories = list(scores.keys())
    values = list(scores.values())

    # Close the radar chart
    categories = categories + [categories[0]]
    values = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(102, 126, 234, 0.3)",
            line=dict(color="rgb(102, 126, 234)", width=2),
            name="Your Score",
        )
    )

    # Add benchmark line (70% as "good")
    benchmark = [70] * len(categories)
    fig.add_trace(
        go.Scatterpolar(
            r=benchmark,
            theta=categories,
            fill="none",
            line=dict(color="rgba(156, 163, 175, 0.5)", width=1, dash="dash"),
            name="Target (70%)",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")),
        showlegend=True,
        title=dict(text=title, x=0.5),
        height=400,
    )

    return fig


def create_skill_heatmap(skill_gaps: Dict[str, Dict]) -> go.Figure:
    """Create a heatmap showing skill coverage by category."""
    categories = []
    coverages = []
    missing_counts = []

    for category, data in skill_gaps.items():
        if category != "uncategorized":
            categories.append(category.split("/")[-1])  # Just the subcategory
            coverages.append(data.get("coverage", 0) * 100)
            missing_counts.append(len(data.get("missing", [])))

    if not categories:
        return None

    fig = go.Figure(
        data=go.Bar(
            x=categories,
            y=coverages,
            marker=dict(
                color=coverages,
                colorscale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#10b981"]],
                showscale=True,
                colorbar=dict(title="Coverage %"),
            ),
            text=[f"{c:.0f}%" for c in coverages],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Coverage: %{y:.0f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title="Skill Coverage by Category",
        xaxis_title="Skill Category",
        yaxis_title="Coverage (%)",
        yaxis=dict(range=[0, 110]),
        height=350,
    )

    return fig


def create_score_breakdown(components: List[Dict]) -> go.Figure:
    """Create a horizontal bar chart for score component breakdown."""
    names = [c["name"] for c in components]
    scores = [c["score"] for c in components]
    weighted = [c["weighted_score"] for c in components]

    # Assign colors based on score
    colors = []
    for s in scores:
        if s >= 80:
            colors.append("#10b981")
        elif s >= 60:
            colors.append("#3b82f6")
        elif s >= 40:
            colors.append("#f59e0b")
        else:
            colors.append("#ef4444")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=names,
            x=scores,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{s:.0f}%" for s in scores],
            textposition="inside",
            name="Component Score",
            hovertemplate="<b>%{y}</b><br>Score: %{x:.0f}%<br>Contributes: %{customdata:.1f} pts<extra></extra>",
            customdata=weighted,
        )
    )

    # Add target line
    fig.add_vline(
        x=70,
        line_dash="dash",
        line_color="gray",
        annotation_text="Target (70%)",
        annotation_position="top",
    )

    fig.update_layout(
        title="Score Components",
        xaxis_title="Score (%)",
        xaxis=dict(range=[0, 105]),
        height=300,
        showlegend=False,
    )

    return fig


def create_experience_relevance_chart(experience_data: List[Dict]) -> go.Figure:
    """Create chart showing relevance of experience bullets."""
    if not experience_data:
        return None

    # Truncate text for display
    texts = [
        e["text"][:50] + "..." if len(e["text"]) > 50 else e["text"]
        for e in experience_data[:10]
    ]
    relevance = [e["relevance"] * 100 for e in experience_data[:10]]

    colors = []
    for r in relevance:
        if r >= 70:
            colors.append("#10b981")
        elif r >= 50:
            colors.append("#3b82f6")
        elif r >= 30:
            colors.append("#f59e0b")
        else:
            colors.append("#ef4444")

    fig = go.Figure(
        go.Bar(
            y=texts,
            x=relevance,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{r:.0f}%" for r in relevance],
            textposition="inside",
        )
    )

    fig.update_layout(
        title="Experience Bullet Relevance to Job",
        xaxis_title="Relevance (%)",
        xaxis=dict(range=[0, 105]),
        height=max(250, len(texts) * 35),
        margin=dict(l=200),
    )

    return fig

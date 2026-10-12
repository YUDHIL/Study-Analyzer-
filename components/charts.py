"""
components/charts.py - Plotly chart creators with inspiring, high-contrast focus theme.
"""

from typing import List, Dict, Any
import plotly.graph_objects as go


def apply_theme(fig: go.Figure, height: int = 280, title_text: str = "") -> go.Figure:
    """Apply an inspiring, luminous dark focus theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94a3b8", size=12),
        margin=dict(l=30, r=20, t=45, b=35),
        height=height,
        legend=dict(
            font=dict(color="#e2e8f0"),
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="rgba(255, 255, 255, 0.1)"
        )
    )
    if title_text:
        fig.update_layout(
            title=dict(
                text=f"<b>{title_text}</b>",
                font=dict(color="#ffffff", size=14, family="Plus Jakarta Sans, sans-serif")
            )
        )
    fig.update_xaxes(
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        tickfont=dict(color="#94a3b8", size=11)
    )
    fig.update_yaxes(
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        tickfont=dict(color="#94a3b8", size=11)
    )
    return fig


def create_subject_completion_chart(subjects_breakdown: List[Dict[str, Any]]) -> go.Figure:
    """Horizontal bar chart showing syllabus completion percentage by subject with progress color grading."""
    fig = go.Figure()
    if not subjects_breakdown:
        return apply_theme(fig, height=280, title_text="No Subjects Available")

    subjs = list(reversed(subjects_breakdown))
    names = [f"<b>{s['subject_code']}</b> • {s['subject_name']}" for s in subjs]
    pcts = [s["completion_percentage"] for s in subjs]

    # Glowing color hierarchy
    colors = [
        "#10b981" if p >= 75 else "#06b6d4" if p >= 40 else "#f59e0b" if p >= 15 else "#64748b"
        for p in pcts
    ]

    fig.add_trace(go.Bar(
        x=pcts,
        y=names,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(255, 255, 255, 0.15)", width=1)
        ),
        text=[f"<b>{p}%</b>" for p in pcts],
        textposition="outside",
        textfont=dict(color="#f8fafc", size=11),
        cliponaxis=False
    ))

    apply_theme(fig, height=280, title_text="Syllabus Completion by Subject")
    fig.update_xaxes(range=[0, 108], title="Completed Topics (%)")
    fig.update_yaxes(autorange=True)
    return fig


def create_daily_study_chart(daily_hours_dict: Dict[str, float], target_hours: float = 3.0) -> go.Figure:
    """Bar chart showing daily study hours with a vibrant target line and goal completions."""
    fig = go.Figure()
    dates = list(daily_hours_dict.keys())
    hours = list(daily_hours_dict.values())

    labels = [d.split("-")[1] + "/" + d.split("-")[2] if "-" in d else d for d in dates]
    colors = ["#10b981" if h >= target_hours else "#0ea5e9" for h in hours]

    fig.add_trace(go.Bar(
        x=labels,
        y=hours,
        name="Actual Hours",
        marker=dict(
            color=colors,
            line=dict(color="rgba(255, 255, 255, 0.15)", width=1)
        ),
        text=[f"<b>{h:.1f}h</b>" for h in hours],
        textposition="outside",
        textfont=dict(color="#f8fafc", size=11)
    ))

    # Glowing amber target threshold
    fig.add_hline(
        y=target_hours,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=2,
        annotation_text=f"🎯 Target: {target_hours}h",
        annotation_position="top right",
        annotation_font=dict(color="#fbbf24", size=11, family="Plus Jakarta Sans, sans-serif")
    )

    max_val = max(hours + [target_hours]) + 1.2
    apply_theme(fig, height=280, title_text="Daily Study Hours (Last 7 Days)")
    fig.update_yaxes(range=[0, max_val], title="Hours Logged")
    fig.update_xaxes(title="Date")
    fig.update_layout(showlegend=False)
    return fig


def create_subject_distribution_pie(subject_hours: Dict[str, float]) -> go.Figure:
    """Vibrant donut chart of study time distribution across subjects."""
    fig = go.Figure()
    if not subject_hours or sum(subject_hours.values()) == 0:
        return apply_theme(fig, height=280, title_text="No Study Sessions Recorded")

    labels = list(subject_hours.keys())
    values = list(subject_hours.values())
    palette = ["#0ea5e9", "#10b981", "#8b5cf6", "#f59e0b", "#f43f5e", "#14b8a6"]

    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(
            colors=palette[:len(labels)],
            line=dict(color="#090e1c", width=2)
        ),
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans, sans-serif")
    ))

    apply_theme(fig, height=280, title_text="Study Time Distribution")
    fig.update_layout(showlegend=False)
    return fig


def create_test_trend_chart(test_results: List[Dict[str, Any]]) -> go.Figure:
    """Scatter/line chart of test percentage performance over time with vibrant glowing dots."""
    fig = go.Figure()
    if not test_results:
        return apply_theme(fig, height=300, title_text="No Test Results Recorded")

    sorted_tests = sorted(test_results, key=lambda x: x["test_date"])
    dates = [t["test_date"] for t in sorted_tests]
    pcts = [(t["score"] / t["max_score"] * 100.0) for t in sorted_tests]
    names = [f"{t.get('subject_code', '')}: {t['test_name']}" for t in sorted_tests]

    fig.add_trace(go.Scatter(
        x=dates,
        y=pcts,
        mode="lines+markers+text",
        text=[f"<b>{p:.1f}%</b>" for p in pcts],
        textposition="top center",
        line=dict(color="#38bdf8", width=3, shape="spline"),
        marker=dict(color="#10b981", size=10, line=dict(color="#ffffff", width=2)),
        hovertext=names,
        hoverinfo="text+y"
    ))

    fig.add_hline(
        y=60.0,
        line_dash="dot",
        line_color="#f43f5e",
        annotation_text="Passing Baseline (60%)",
        annotation_font=dict(color="#fb7185", size=11)
    )

    apply_theme(fig, height=300, title_text="Test Performance Trend")
    fig.update_yaxes(range=[0, 115], title="Score Percentage (%)")
    fig.update_xaxes(title="Test Date")
    fig.update_layout(showlegend=False)
    return fig


def create_coding_concepts_chart(concept_breakdown: List[Dict[str, Any]]) -> go.Figure:
    """Grouped bar chart showing Attempted, Solved, and Independently Solved by concept."""
    fig = go.Figure()
    if not concept_breakdown:
        return apply_theme(fig, height=300, title_text="No Coding Logs Recorded")

    concepts = [c["concept"] for c in concept_breakdown]
    attempted = [c["attempted"] for c in concept_breakdown]
    solved = [c["solved"] for c in concept_breakdown]
    independent = [c["independent"] for c in concept_breakdown]

    fig.add_trace(go.Bar(
        name="Attempted",
        x=concepts,
        y=attempted,
        marker=dict(color="#475569")
    ))
    fig.add_trace(go.Bar(
        name="Solved",
        x=concepts,
        y=solved,
        marker=dict(color="#0ea5e9")
    ))
    fig.add_trace(go.Bar(
        name="Independent (No Hints)",
        x=concepts,
        y=independent,
        marker=dict(color="#10b981")
    ))

    apply_theme(fig, height=300, title_text="Python Coding Progress by Concept")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Problems Count")
    fig.update_xaxes(title="Concept")
    return fig

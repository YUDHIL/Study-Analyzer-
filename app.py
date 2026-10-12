"""
app.py - Main Dashboard for Study Analyzer.

Personal productivity and academic analytics application for semester exam
preparation, daily study logging, and Python practice tracking.
"""

import streamlit as st
from datetime import date, datetime
import database
import analytics
import recommendations
from components.theme import inject_focus_theme, render_focus_hero
from components.sidebar import render_sidebar
from components.metrics import render_metric_card, render_empty_state, render_html
from components.charts import (
    create_subject_completion_chart,
    create_daily_study_chart,
    create_subject_distribution_pie,
    create_coding_concepts_chart
)

# Page Configuration
st.set_page_config(
    page_title="Study Analyzer | Focus & Academic Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
database.init_db()

# Inject Global Aesthetic & Motivation Focus Theme
inject_focus_theme()

# Render unified sidebar
render_sidebar()

# Focus Hero Banner
today_str = date.today().strftime("%A, %B %d, %Y")
render_focus_hero(
    title="Study Command Center",
    subtitle=f"Welcome to your deep focus workspace. Today is {today_str}. Build momentum with every focused block."
)

# 1. Top Metric Cards
syllabus_data = analytics.calculate_syllabus_completion()
study_data = analytics.calculate_study_hours()
test_data = analytics.calculate_test_metrics()
coding_data = analytics.calculate_coding_metrics()
countdown = analytics.get_exam_countdown()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    days_left = countdown.get("days_to_next")
    days_display = f"{days_left} Days" if days_left is not None else "Passed"
    next_ex = countdown.get("next_exam")
    badge_txt = next_ex["code"] if next_ex else ""
    render_metric_card("Next Exam", days_display, f"{next_ex['name'] if next_ex else 'All complete'}", badge=badge_txt, color="#f59e0b")

with col2:
    render_metric_card("Study Hours", f"{study_data['total_hours']}h", f"{study_data['sessions_count']} logged sessions", badge="Actual Effort", color="#38bdf8")

with col3:
    render_metric_card("Syllabus Done", f"{syllabus_data['overall_percentage']}%", f"{syllabus_data['completed_topics']} of {syllabus_data['total_topics']} topics", badge="Progress", color="#10b981")

with col4:
    test_score_display = f"{test_data['average_percentage']}%" if test_data["total_tests"] > 0 else "N/A"
    test_sub = f"{test_data['total_tests']} tests taken" if test_data["total_tests"] > 0 else "No tests recorded"
    render_metric_card("Avg Test Score", test_score_display, test_sub, badge="Accuracy", color="#8b5cf6")

with col5:
    render_metric_card("Python Solved", str(coding_data["total_independent"]), f"{coding_data['independent_solve_rate']}% independent rate", badge=f"{coding_data['total_attempted']} att.", color="#06b6d4")

st.markdown("<br>", unsafe_allow_html=True)

# 2. Actionable Recommendations
st.markdown("### 💡 Strategic Next Actions")
recs = recommendations.generate_recommendations()

if recs:
    rec_cols = st.columns(min(len(recs), 3))
    for idx, r in enumerate(recs[:3]):
        with rec_cols[idx]:
            border_color = "#f43f5e" if r["priority"] == "High" else "#f59e0b" if r["priority"] == "Medium" else "#0ea5e9"
            render_html(f"""
<div style="background: linear-gradient(145deg, rgba(20, 29, 47, 0.7) 0%, rgba(13, 19, 33, 0.8) 100%); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {border_color}; border-radius: 12px; padding: 16px; height: 155px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.4);">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-weight: 700; color: #ffffff; font-size: 0.95rem;">{r['title']}</span>
<span style="background-color: {border_color}22; color: {border_color}; border: 1px solid {border_color}44; font-size: 0.7rem; padding: 2px 8px; border-radius: 9999px; font-weight: 700;">{r['category']}</span>
</div>
<p style="color: #cbd5e1; font-size: 0.82rem; margin: 0; line-height: 1.38;">{r['message']}</p>
</div>
</div>
""")
else:
    render_empty_state("All targets and preparation tasks on track! Keep up the momentum.")

st.markdown("<br>", unsafe_allow_html=True)

# 3. Interactive Charts (Syllabus & Daily Study)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_comp = create_subject_completion_chart(syllabus_data["subjects_breakdown"])
    st.plotly_chart(fig_comp, use_container_width=True)

with chart_col2:
    acad_target = float(database.get_setting("daily_academic_target_hours", "3.0"))
    fig_daily = create_daily_study_chart(study_data["daily_hours_last_7_days"], target_hours=acad_target)
    st.plotly_chart(fig_daily, use_container_width=True)

# 4. Two-Column Dashboard Panels: Today's Tasks & Weak Topics
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### 📋 Today's Planned Tasks")
    today_iso = date.today().isoformat()
    today_tasks = database.get_tasks_by_date(today_iso)
    
    if today_tasks:
        for t in today_tasks:
            pri_color = "#f43f5e" if t["priority"] == "High" else "#f59e0b" if t["priority"] == "Medium" else "#38bdf8"
            done_icon = "✅" if t["completed"] else "⏳"
            strike = "text-decoration: line-through; opacity: 0.55;" if t["completed"] else ""
            render_html(f"""
<div style="background: rgba(20, 29, 47, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; {strike}">
<div>
<span style="margin-right: 8px;">{done_icon}</span>
<strong style="color: #ffffff; font-size: 0.92rem;">{t['title']}</strong>
<div style="font-size: 0.78rem; color: #94a3b8; margin-top: 2px;">
📂 {t['category']} • 🏷️ {t.get('subject_code', 'General')} • ⏱️ {t['planned_minutes']} mins
</div>
</div>
<span style="color: {pri_color}; font-size: 0.75rem; font-weight: 700; background: {pri_color}18; border: 1px solid {pri_color}44; padding: 2px 8px; border-radius: 6px;">{t['priority']}</span>
</div>
""")
    else:
        render_empty_state("No tasks scheduled for today.", "Head to '1_Daily_Planner' to schedule today's study goals.")

with col_right:
    st.markdown("### ⚠️ Weak Topics Requiring Revision")
    weak_topics = analytics.get_weak_topics(min_confidence=2)
    if weak_topics:
        for wt in weak_topics[:5]:
            status_badge = "#f43f5e" if wt["status"] == "Needs Revision" else "#f59e0b"
            render_html(f"""
<div style="background: rgba(20, 29, 47, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<strong style="color: #ffffff; font-size: 0.92rem;">{wt['topic_name']}</strong>
<span style="color: {status_badge}; background: {status_badge}18; border: 1px solid {status_badge}44; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{wt['status']}</span>
</div>
<div style="font-size: 0.78rem; color: #94a3b8; margin-top: 3px;">
{wt['subject_code']} • {wt['unit_name']} • Confidence: <b style="color: #38bdf8;">{wt['confidence']}/5</b>
</div>
</div>
""")
    else:
        render_empty_state("No topics marked 'Needs Revision' or low confidence.", "Update topic confidence in '2_Subjects_and_Topics'.")

# 5. Study Distribution and Coding Overview
st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.08); margin: 28px 0;'>", unsafe_allow_html=True)
dist_col1, dist_col2 = st.columns(2)

with dist_col1:
    fig_pie = create_subject_distribution_pie(study_data["subject_hours"])
    st.plotly_chart(fig_pie, use_container_width=True)

with dist_col2:
    fig_coding = create_coding_concepts_chart(coding_data["concept_breakdown"])
    st.plotly_chart(fig_coding, use_container_width=True)

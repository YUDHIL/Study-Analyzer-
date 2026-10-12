"""
pages/3_Study_Log.py - Actual study session logging, history tracking, and time analytics.
"""

import streamlit as st
from datetime import date, timedelta
import database
import analytics
from components.theme import inject_focus_theme
from components.sidebar import render_sidebar
from components.metrics import render_header, render_metric_card, render_empty_state
from components.charts import create_daily_study_chart, create_subject_distribution_pie

st.set_page_config(page_title="Study Log | Study Analyzer", page_icon="⏱️", layout="wide")
database.init_db()
inject_focus_theme()
render_sidebar()

render_header("Study Log", "Record actual study sessions independently of planned tasks to analyze real effort.")

# Top Metrics & Summary
study_metrics = analytics.calculate_study_hours()
today_iso = date.today().isoformat()
today_logs = database.get_study_logs(start_date=today_iso, end_date=today_iso)
today_mins = sum(l["minutes"] for l in today_logs)

m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Total Hours Logged", f"{study_metrics['total_hours']}h", f"{study_metrics['sessions_count']} total sessions", color="#38bdf8")
with m2:
    render_metric_card("Today Studied", f"{round(today_mins / 60, 1)}h", f"{today_mins} minutes today", color="#34d399")
with m3:
    acad_target = float(database.get_setting("daily_academic_target_hours", "3.0"))
    render_metric_card("Daily Target", f"{acad_target}h", "Configured daily target", color="#f59e0b")
with m4:
    consist_data = analytics.calculate_study_consistency(
        start_date=(date.today() - timedelta(days=6)).isoformat(),
        end_date=today_iso,
        target_daily_hours=acad_target
    )
    render_metric_card("7-Day Consistency", f"{consist_data['consistency_percentage']}%", f"{consist_data['days_meeting_target']}/{consist_data['elapsed_days']} target days met", color="#a78bfa")

st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

# Form to Log Study Session
with st.expander("📝 Log a Study Session", expanded=True):
    subjects = database.get_all_subjects()
    subject_map = {None: "General / Non-Academic"}
    for s in subjects:
        subject_map[s["id"]] = f"{s['code']} - {s['name']}"

    with st.form("log_session_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            log_date = st.date_input("Study Date", value=date.today())
        with c2:
            chosen_sub_id = st.selectbox(
                "Subject",
                options=list(subject_map.keys()),
                format_func=lambda x: subject_map[x]
            )
        with c3:
            minutes = st.number_input("Duration (Minutes)", min_value=5, max_value=720, value=60, step=15)

        c4, c5 = st.columns([2, 1])
        with c4:
            topic = st.text_input("Topic / Concept Studied", placeholder="e.g. MapReduce word count and combiner optimization")
        with c5:
            understanding = st.slider("Understanding Rating (1 = Poor, 5 = Mastered)", min_value=1, max_value=5, value=4)

        notes = st.text_area("Key Takeaways / Notes (Optional)", placeholder="Summarize key points, doubts, or formulas reviewed...")

        submit_log = st.form_submit_button("Record Study Session", use_container_width=True)
        if submit_log:
            if minutes <= 0:
                st.error("Study duration must be positive.")
            else:
                database.add_study_log(
                    study_date=log_date.isoformat(),
                    subject_id=chosen_sub_id,
                    topic=topic,
                    minutes=minutes,
                    understanding=understanding,
                    notes=notes
                )
                st.success(f"Logged {minutes} minutes of study!")
                st.rerun()

st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

# Visualizations: Recent Study Hours & Subject Distribution
v_col1, v_col2 = st.columns(2)
with v_col1:
    fig_daily = create_daily_study_chart(study_metrics["daily_hours_last_7_days"], target_hours=acad_target)
    st.plotly_chart(fig_daily, use_container_width=True)
with v_col2:
    fig_pie = create_subject_distribution_pie(study_metrics["subject_hours"])
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

# Study Session History Table & Filters
st.subheader("📜 Study Session History")

f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    start_filter = st.date_input("From Date", value=date.today() - timedelta(days=30))
with f_col2:
    end_filter = st.date_input("To Date", value=date.today())
with f_col3:
    sub_filter = st.selectbox(
        "Filter by Subject",
        options=["All Subjects"] + [s["code"] for s in subjects]
    )

selected_sub_filter_id = None
if sub_filter != "All Subjects":
    match_sub = next((s["id"] for s in subjects if s["code"] == sub_filter), None)
    selected_sub_filter_id = match_sub

logs = database.get_study_logs(
    start_date=start_filter.isoformat(),
    end_date=end_filter.isoformat(),
    subject_id=selected_sub_filter_id
)

if logs:
    st.caption(f"Showing {len(logs)} session(s) totaling {round(sum(l['minutes'] for l in logs)/60, 1)} hours:")
    for l in logs:
        l_c1, l_c2, l_c3, l_c4 = st.columns([2, 4, 2, 1])
        with l_c1:
            st.markdown(f"**{l['study_date']}**")
            st.caption(f"{l['minutes']} mins ({round(l['minutes']/60, 1)}h)")
        with l_c2:
            st.markdown(f"**{l.get('subject_code') or 'General'}**: {l['topic'] or 'General Study'}")
            if l['notes']:
                st.caption(f"📝 {l['notes']}")
        with l_c3:
            st.markdown(f"Understanding: **{'⭐' * l['understanding']}** ({l['understanding']}/5)")
        with l_c4:
            if st.button("🗑️", key=f"del_log_{l['id']}", help="Delete entry"):
                database.delete_study_log(l["id"])
                st.rerun()
        st.markdown("<hr style='border-color: #1e293b; margin: 4px 0;'>", unsafe_allow_html=True)
else:
    render_empty_state("No study sessions match the selected filters.", "Use the form above to log your study sessions.")

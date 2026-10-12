"""
pages/4_Test_Performance.py - Test marks recording, score analytics, and trend visualization.
"""

import streamlit as st
from datetime import date
import database
import analytics
from components.theme import inject_focus_theme
from components.sidebar import render_sidebar
from components.metrics import render_header, render_metric_card, render_empty_state, render_html
from components.charts import create_test_trend_chart

st.set_page_config(page_title="Test Performance | Study Analyzer", page_icon="📊", layout="wide")
database.init_db()
inject_focus_theme()
render_sidebar()

render_header("Test Performance", "Record mock tests, quizzes, and CIE assessments to pinpoint academic weak spots.")

test_metrics = analytics.calculate_test_metrics()

# Summary Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Total Tests", str(test_metrics["total_tests"]), "Assessments recorded", color="#38bdf8")
with m2:
    avg_display = f"{test_metrics['average_percentage']}%" if test_metrics["total_tests"] > 0 else "N/A"
    render_metric_card("Average Score", avg_display, "Mean percentage of all tests", color="#34d399")
with m3:
    weighted_display = f"{test_metrics['weighted_percentage']}%" if test_metrics["total_tests"] > 0 else "N/A"
    render_metric_card("Weighted Score", weighted_display, "Total marks / Max marks", color="#a78bfa")
with m4:
    weak_sub = test_metrics["subject_performance"][0] if test_metrics["subject_performance"] else None
    weak_label = f"{weak_sub['subject_code']} ({weak_sub['average_percentage']}%)" if weak_sub else "None"
    render_metric_card("Needs Focus", weak_label, "Subject with lowest average", color="#ef4444" if weak_sub else "#64748b")

st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

# Add Test Result Form
with st.expander("📝 Record a New Test Result", expanded=test_metrics["total_tests"] == 0):
    subjects = database.get_all_subjects()
    if subjects:
        with st.form("add_test_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                test_name = st.text_input("Test / Quiz Name", placeholder="e.g. Unit Test 1 - Module 1 & 2")
            with c2:
                sub_id = st.selectbox(
                    "Subject",
                    options=[s["id"] for s in subjects],
                    format_func=lambda x: next((f"{s['code']} - {s['name']}" for s in subjects if s["id"] == x), "")
                )
            with c3:
                test_date = st.date_input("Test Date", value=date.today())

            c4, c5, c6 = st.columns([1, 1, 2])
            with c4:
                score = st.number_input("Score Obtained", min_value=0.0, max_value=500.0, value=20.0, step=0.5)
            with c5:
                max_score = st.number_input("Maximum Marks", min_value=1.0, max_value=500.0, value=25.0, step=1.0)
            with c6:
                notes = st.text_input("Notes / Mistakes to review", placeholder="e.g. Need to review DES key schedule formulas")

            submit_test = st.form_submit_button("Record Test Result", use_container_width=True)
            if submit_test:
                if not test_name.strip():
                    st.error("Test name cannot be empty.")
                elif score > max_score:
                    st.error(f"Score ({score}) cannot be greater than maximum marks ({max_score}).")
                else:
                    database.add_test_result(
                        test_date=test_date.isoformat(),
                        subject_id=sub_id,
                        test_name=test_name,
                        score=score,
                        max_score=max_score,
                        notes=notes
                    )
                    pct = round((score / max_score) * 100, 1)
                    st.success(f"Recorded '{test_name}' with score {score}/{max_score} ({pct}%)!")
                    st.rerun()
    else:
        st.warning("Please configure subjects first before recording tests.")

# Performance Trend Chart
all_tests = database.get_test_results()
if all_tests:
    st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    st.plotly_chart(create_test_trend_chart(all_tests), use_container_width=True)

# Subject-Wise Performance Breakdown Table
st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
st.subheader("📊 Subject-Wise Assessment Breakdown")

if test_metrics["subject_performance"]:
    p_col1, p_col2 = st.columns([3, 2])
    with p_col1:
        for sp in test_metrics["subject_performance"]:
            badge_color = "#34d399" if sp["average_percentage"] >= 75 else "#f59e0b" if sp["average_percentage"] >= 60 else "#ef4444"
            status_text = "Adequate Data" if sp["test_count"] >= 2 else "Limited Data (1 test)"
            render_html(f"""
<div style="background-color: #1e293b; border-left: 4px solid {badge_color}; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<strong style="color: #f8fafc; font-size: 1rem;">{sp['subject_code']} - {sp['subject_name']}</strong>
<span style="font-size: 1.1rem; font-weight: 700; color: {badge_color};">{sp['average_percentage']}% avg</span>
</div>
<div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
{sp['test_count']} test(s) taken • Weighted Score: {sp['weighted_percentage']}% • <span style="color: #64748b;">{status_text}</span>
</div>
</div>
""")
    with p_col2:
        render_html("""
<div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px;">
<h4 style="color: #f8fafc; margin-top: 0;">Evaluation Methodology</h4>
<p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.4;">
• <strong>Average Percentage:</strong> The arithmetic mean of percentage scores across all tests for that subject.<br>
• <strong>Weighted Percentage:</strong> Total points scored divided by total points possible.<br>
• Subjects with fewer than 2 tests are labeled with <em>Limited Data</em> to avoid premature academic conclusions.
</p>
</div>
""")
else:
    render_empty_state("No assessments recorded yet.", "Add your test marks above to unlock subject-wise performance analysis.")

# Test History Table
st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
st.subheader("📜 Assessment History")
if all_tests:
    for t in all_tests:
        pct = round((t["score"] / t["max_score"]) * 100, 1)
        color = "#34d399" if pct >= 75 else "#f59e0b" if pct >= 60 else "#ef4444"
        c1, c2, c3, c4 = st.columns([2, 4, 2, 1])
        with c1:
            st.markdown(f"**{t['test_date']}**")
            st.caption(f"{t['subject_code']}")
        with c2:
            st.markdown(f"**{t['test_name']}**")
            if t["notes"]:
                st.caption(f"📝 {t['notes']}")
        with c3:
            st.markdown(f"<span style='color: {color}; font-weight: 700; font-size: 1.1rem;'>{t['score']} / {t['max_score']}</span> ({pct}%)", unsafe_allow_html=True)
        with c4:
            if st.button("🗑️", key=f"del_test_{t['id']}", help="Delete test result"):
                database.delete_test_result(t["id"])
                st.rerun()
        st.markdown("<hr style='border-color: #1e293b; margin: 4px 0;'>", unsafe_allow_html=True)

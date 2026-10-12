"""
pages/6_Weekly_Analytics.py - Seven-day comparative reports, trends, and database backup/restore.
"""

import streamlit as st
from datetime import date, timedelta
import os
import tempfile
import database
import analytics
from components.theme import inject_focus_theme
from components.sidebar import render_sidebar
from components.metrics import render_header, render_metric_card, render_empty_state, render_html
from components.charts import create_daily_study_chart, create_subject_distribution_pie

st.set_page_config(page_title="Weekly Analytics | Study Analyzer", page_icon="📈", layout="wide")
database.init_db()
inject_focus_theme()
render_sidebar()

render_header("Weekly Analytics & Backup", "Comprehensive 7-day progress reports, comparative trends, and local data safety.")

tab1, tab2 = st.tabs(["📊 7-Day Performance Report", "💾 Database Backup & Restore"])

with tab1:
    # Date Range Selector (default: last 7 days including today)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        default_start = date.today() - timedelta(days=6)
        rep_start = st.date_input("Report Start Date", value=default_start)
    with col_d2:
        rep_end = st.date_input("Report End Date", value=date.today())

    start_str = rep_start.isoformat()
    end_str = rep_end.isoformat()

    report = analytics.get_weekly_analytics_report(start_str, end_str)

    # Top Comparative Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_str = f"{report['hours_delta']:+0.1f}h vs prior" if report['previous_hours'] > 0 else "Baseline week"
        render_metric_card("Study Hours", f"{report['current_hours']}h", delta_str, color="#38bdf8")
    with c2:
        render_metric_card("Task Completion", f"{report['task_completion_rate']}%", f"{report['tasks_completed']}/{report['tasks_total']} tasks done", color="#34d399")
    with c3:
        ind_pct = round((report['coding_independent'] / report['coding_attempted'] * 100), 1) if report['coding_attempted'] > 0 else 0.0
        render_metric_card("Coding Solved", f"{report['coding_solved']}", f"{report['coding_independent']} independent ({ind_pct}%)", color="#2dd4bf")
    with c4:
        acad_target = float(database.get_setting("daily_academic_target_hours", "3.0"))
        consistency = analytics.calculate_study_consistency(start_str, end_str, target_daily_hours=acad_target)
        render_metric_card("Study Consistency", f"{consistency['consistency_percentage']}%", f"{consistency['days_meeting_target']}/{consistency['elapsed_days']} target days met", color="#a78bfa")

    st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

    # Charts for selected period
    v1, v2 = st.columns(2)
    with v1:
        # Build daily map for selected period
        logs = database.get_study_logs(start_date=start_str, end_date=end_str)
        daily_dict = {}
        curr_d = rep_start
        while curr_d <= rep_end:
            d_s = curr_d.isoformat()
            d_mins = sum(l["minutes"] for l in logs if l["study_date"] == d_s)
            daily_dict[d_s] = round(d_mins / 60.0, 1)
            curr_d += timedelta(days=1)
        fig_daily = create_daily_study_chart(daily_dict, target_hours=acad_target)
        st.plotly_chart(fig_daily, use_container_width=True)

    with v2:
        sub_hours_map = {d["subject"]: d["hours"] for d in report["subject_distribution"]}
        fig_pie = create_subject_distribution_pie(sub_hours_map)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Detailed Comparison Table
    st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    st.subheader("📋 Period Activity Comparison")
    
    render_html(f"""
<table style="width: 100%; border-collapse: collapse; background-color: #1e293b; border-radius: 8px; overflow: hidden;">
<thead style="background-color: #0f172a; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">
<tr>
<th style="padding: 12px 16px; text-align: left;">Metric</th>
<th style="padding: 12px 16px; text-align: right;">Current Period</th>
<th style="padding: 12px 16px; text-align: right;">Previous Period</th>
<th style="padding: 12px 16px; text-align: right;">Change</th>
</tr>
</thead>
<tbody style="color: #f8fafc; font-size: 0.9rem;">
<tr style="border-bottom: 1px solid #334155;">
<td style="padding: 12px 16px;">Total Study Time</td>
<td style="padding: 12px 16px; text-align: right; font-weight: 600;">{report['current_hours']} hrs</td>
<td style="padding: 12px 16px; text-align: right; color: #94a3b8;">{report['previous_hours']} hrs</td>
<td style="padding: 12px 16px; text-align: right; font-weight: 600; color: {'#34d399' if report['hours_delta'] >= 0 else '#ef4444'};">{report['hours_delta']:+0.1f} hrs</td>
</tr>
<tr style="border-bottom: 1px solid #334155;">
<td style="padding: 12px 16px;">Scheduled Tasks Completed</td>
<td style="padding: 12px 16px; text-align: right; font-weight: 600;">{report['tasks_completed']} of {report['tasks_total']}</td>
<td style="padding: 12px 16px; text-align: right; color: #94a3b8;">-</td>
<td style="padding: 12px 16px; text-align: right; font-weight: 600; color: #38bdf8;">{report['task_completion_rate']}% rate</td>
</tr>
<tr>
<td style="padding: 12px 16px;">Python Coding Problems</td>
<td style="padding: 12px 16px; text-align: right; font-weight: 600;">{report['coding_solved']} solved ({report['coding_independent']} indep.)</td>
<td style="padding: 12px 16px; text-align: right; color: #94a3b8;">-</td>
<td style="padding: 12px 16px; text-align: right; font-weight: 600; color: #2dd4bf;">{report['coding_attempted']} attempted</td>
</tr>
</tbody>
</table>
""")

with tab2:
    st.markdown("### 💾 Local SQLite Database Backup & Restore")
    st.caption("All study logs, test results, task schedules, and syllabus progress are stored locally on your machine.")

    b_col1, b_col2 = st.columns(2)
    
    with b_col1:
        st.markdown("#### Export Backup")
        st.write("Download an atomic backup snapshot of your study database:")
        db_path = database.get_db_path()
        if os.path.exists(db_path):
            with open(db_path, "rb") as fp:
                db_bytes = fp.read()
            backup_filename = f"study_analyzer_backup_{date.today().isoformat()}.db"
            st.download_button(
                label="📥 Download Database Backup (.db)",
                data=db_bytes,
                file_name=backup_filename,
                mime="application/x-sqlite3",
                use_container_width=True
            )
        else:
            st.info("Database file not yet created.")

    with b_col2:
        st.markdown("#### Restore from Backup")
        st.write("Upload a previously saved `.db` backup file to restore records:")
        uploaded_backup = st.file_uploader("Select SQLite Backup (.db)", type=["db", "sqlite", "sqlite3"])
        
        if uploaded_backup is not None:
            with st.popover("⚠️ Confirm Restoration"):
                st.warning("Restoring will replace current records with the backup file data. Are you sure you wish to proceed?")
                if st.button("Yes, Restore Database", type="primary", use_container_width=True):
                    try:
                        # Write uploaded content to a temp file and test schema
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                            tmp.write(uploaded_backup.getvalue())
                            tmp_path = tmp.name

                        database.restore_database(tmp_path)
                        os.remove(tmp_path)
                        st.success("Database restored successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Restoration failed: {str(e)}")

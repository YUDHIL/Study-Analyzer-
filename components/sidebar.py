"""
components/sidebar.py - Inspiring sidebar with exam countdown, focus status, and target controls.
"""

import streamlit as st
from datetime import date
import analytics
import database
from components.metrics import render_html


def render_sidebar() -> None:
    """Render unified sidebar with motivating focus status and live countdown."""
    with st.sidebar:
        # App Branding & Focus Mode Status
        render_html("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
<div style="background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #10b981 100%); width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-weight: 800; font-size: 1.25rem; color: #ffffff; box-shadow: 0 4px 16px rgba(14, 165, 233, 0.4);">
⚡
</div>
<div>
<h3 style="margin: 0; font-size: 1.2rem; color: #ffffff; font-weight: 800; letter-spacing: -0.02em;">Study Analyzer</h3>
<div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
<span style="display: inline-block; width: 6px; height: 6px; background-color: #34d399; border-radius: 50%;"></span>
<span style="font-size: 0.72rem; color: #34d399; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Deep Work Active</span>
</div>
</div>
</div>
""")

        st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.08); margin: 12px 0;'>", unsafe_allow_html=True)

        # Examination Countdown Card
        countdown = analytics.get_exam_countdown()
        next_exam = countdown.get("next_exam")
        if next_exam:
            days = next_exam["days_remaining"]
            if days > 0:
                badge_color = "#38bdf8" if days > 14 else "#f59e0b" if days > 5 else "#ef4444"
                render_html(f"""
<div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {badge_color}; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px; box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.4);">
<div style="font-size: 0.72rem; text-transform: uppercase; color: #94a3b8; font-weight: 700; letter-spacing: 0.05em;">Next Examination In</div>
<div style="font-size: 1.85rem; font-weight: 800; color: #ffffff; margin: 4px 0; letter-spacing: -0.03em;">{days} <span style="font-size: 0.95rem; font-weight: 500; color: #94a3b8;">days</span></div>
<div style="font-size: 0.88rem; color: {badge_color}; font-weight: 700;">{next_exam['code']} • {next_exam['name']}</div>
<div style="font-size: 0.75rem; color: #64748b; margin-top: 3px;">📅 Exam Date: {next_exam['exam_date']}</div>
</div>
""")
            elif days == 0:
                st.error(f"🚨 **TODAY:** {next_exam['code']} - {next_exam['name']} Examination!")
            else:
                st.info("Configured semester examinations completed.")

        # Staggered Exam Schedule List
        with st.expander("📅 Semester Exam Timeline", expanded=False):
            subjects = database.get_all_subjects()
            today = date.today()
            for s in subjects:
                try:
                    ex_d = date.fromisoformat(s["exam_date"])
                    diff = (ex_d - today).days
                    badge_style = "color: #34d399;" if diff > 14 else "color: #fbbf24;" if diff > 5 else "color: #f87171;"
                    label = f"{diff}d left" if diff >= 0 else "Passed"
                except Exception:
                    label = "Unset"
                    badge_style = "color: #94a3b8;"
                st.markdown(
                    f"**{s['code']}**: {s['name'][:20]}..  \n"
                    f"<small style='color: #94a3b8;'>{s['exam_date']} • <span style='{badge_style} font-weight: 600;'>{label}</span></small>",
                    unsafe_allow_html=True
                )

        st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.08); margin: 12px 0;'>", unsafe_allow_html=True)

        # Daily Study Targets
        with st.expander("⚙️ Daily Study Targets", expanded=False):
            curr_acad = float(database.get_setting("daily_academic_target_hours", "3.0"))
            curr_code = float(database.get_setting("daily_coding_target_hours", "1.0"))
            
            new_acad = st.number_input("Academic Target (hrs)", min_value=0.5, max_value=12.0, value=curr_acad, step=0.5)
            new_code = st.number_input("Python Target (hrs)", min_value=0.25, max_value=6.0, value=curr_code, step=0.25)
            
            if st.button("Save Daily Targets", use_container_width=True):
                database.set_setting("daily_academic_target_hours", str(new_acad))
                database.set_setting("daily_coding_target_hours", str(new_code))
                st.success("Targets updated!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        render_html("""
<div style="text-align: center; color: #64748b; font-size: 0.75rem; padding: 12px; background: rgba(15, 23, 42, 0.4); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.04);">
<span style="color: #34d399;">●</span> Local SQLite Encrypted & Active<br>
<span style="color: #94a3b8; font-weight: 600;">Study Analyzer v1.0 • 2026</span>
</div>
""")

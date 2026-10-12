"""
pages/1_Daily_Planner.py - Daily study planning, priority scheduling, and overdue tracking.
"""

import streamlit as st
from datetime import date, datetime
import database
import analytics
from components.theme import inject_focus_theme
from components.sidebar import render_sidebar
from components.metrics import render_header, render_metric_card, render_empty_state, render_html

st.set_page_config(page_title="Daily Planner | Study Analyzer", page_icon="📋", layout="wide")
database.init_db()
inject_focus_theme()
render_sidebar()

render_header("Daily Planner", "Plan your study sessions, prioritize tasks, and track planned vs. actual execution.")

# Date Selector & Overview Metrics
top_col1, top_col2 = st.columns([1, 2])
with top_col1:
    selected_date = st.date_input("Select Planning Date", value=date.today())
    selected_date_str = selected_date.isoformat()

# Task & Time Metrics for Selected Date
task_metrics = analytics.calculate_task_metrics(task_date=selected_date_str)

with top_col2:
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        render_metric_card(
            "Tasks Done",
            f"{task_metrics['completed_tasks']}/{task_metrics['total_tasks']}",
            f"{task_metrics['completion_rate']}% completed",
            color="#34d399"
        )
    with m_col2:
        render_metric_card(
            "Planned Time",
            f"{task_metrics['planned_minutes']}m",
            f"{round(task_metrics['planned_minutes'] / 60, 1)} hours",
            color="#38bdf8"
        )
    with m_col3:
        diff = task_metrics["difference_minutes"]
        diff_label = f"+{diff}m over" if diff >= 0 else f"{diff}m deficit"
        render_metric_card(
            "Actual Studied",
            f"{task_metrics['actual_minutes']}m",
            diff_label,
            badge="Logged",
            color="#a78bfa" if diff >= 0 else "#f59e0b"
        )

# Overdue Tasks Alert
overdue = database.get_overdue_tasks(current_date=date.today().isoformat())
if overdue:
    with st.expander(f"⚠️ Overdue Tasks Notice ({len(overdue)} pending from past dates)", expanded=True):
        st.caption("These tasks were scheduled on earlier dates but not completed. Complete or reschedule them below.")
        for ot in overdue:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                st.markdown(f"**{ot['title']}** ({ot['task_date']})")
                st.caption(f"{ot['category']} • {ot.get('subject_code', 'General')}")
            with c2:
                st.write(f"⏱️ {ot['planned_minutes']} mins | Priority: **{ot['priority']}**")
            with c3:
                if st.button("Mark Completed", key=f"overdue_done_{ot['id']}"):
                    database.toggle_task_completion(ot['id'], True)
                    st.rerun()
            with c4:
                if st.button("Reschedule Today", key=f"overdue_resched_{ot['id']}"):
                    database.update_task(ot['id'], date.today().isoformat(), ot['title'], ot['category'], ot['subject_id'], ot['planned_minutes'], ot['priority'])
                    st.rerun()

st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

# Add New Task & Priority Planner
tab1, tab2 = st.tabs(["➕ Add New Task", "⚡ Auto-Generate Priority Plan"])

subjects = database.get_all_subjects()
subject_options = {None: "None / General"}
for s in subjects:
    subject_options[s["id"]] = f"{s['code']} - {s['name']}"

with tab1:
    with st.form("add_task_form", clear_on_submit=True):
        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col1:
            title = st.text_input("Task Title", placeholder="e.g. Study Module 2: Sensors & Sensor Networks")
        with f_col2:
            category = st.selectbox(
                "Category",
                ["Semester Study", "Revision", "Practice Test", "Python Coding", "DSA Practice", "Project Work"]
            )
        with f_col3:
            chosen_sub_id = st.selectbox(
                "Associated Subject",
                options=list(subject_options.keys()),
                format_func=lambda x: subject_options[x]
            )

        f_col4, f_col5, f_col6 = st.columns(3)
        with f_col4:
            planned_minutes = st.number_input("Estimated Minutes", min_value=10, max_value=480, value=60, step=15)
        with f_col5:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        with f_col6:
            st.write("")
            st.write("")
            submit_task = st.form_submit_button("Add Task to Plan", use_container_width=True)

        if submit_task:
            if not title.strip():
                st.error("Task title cannot be empty.")
            else:
                database.add_task(
                    task_date=selected_date_str,
                    title=title,
                    category=category,
                    subject_id=chosen_sub_id,
                    planned_minutes=planned_minutes,
                    priority=priority
                )
                st.success("Task added to schedule!")
                st.rerun()

with tab2:
    st.markdown("#### Smart Priority Planner")
    st.write(
        "Automatically creates a structured study plan based on: "
        "(1) upcoming exam urgency, (2) weak or uncompleted topics, and (3) daily Python coding target."
    )
    if st.button("Generate Suggested Plan for Selected Date", type="primary"):
        countdown = analytics.get_exam_countdown()
        next_exam = countdown.get("next_exam")
        weak_topics = analytics.get_weak_topics(min_confidence=2)
        
        created_count = 0
        # 1. Upcoming exam priority task
        if next_exam:
            database.add_task(
                task_date=selected_date_str,
                title=f"Complete high-priority topic for {next_exam['code']} ({next_exam['name']})",
                category="Semester Study",
                subject_id=next_exam["id"],
                planned_minutes=90,
                priority="High"
            )
            created_count += 1
            
        # 2. Weak topic revision task
        if weak_topics:
            wt = weak_topics[0]
            database.add_task(
                task_date=selected_date_str,
                title=f"Revise weak concept: {wt['topic_name']} ({wt['unit_name']})",
                category="Revision",
                subject_id=wt["subject_id"],
                planned_minutes=45,
                priority="High"
            )
            created_count += 1

        # 3. Daily Python practice task
        database.add_task(
            task_date=selected_date_str,
            title="Solve 1-2 Python practice problems independently",
            category="Python Coding",
            subject_id=None,
            planned_minutes=45,
            priority="Medium"
        )
        created_count += 1

        st.success(f"Generated {created_count} prioritized tasks! You can review, edit, or check them off below.")
        st.rerun()

st.markdown("<hr style='border-color: #334155; margin: 24px 0;'>", unsafe_allow_html=True)

# Task List for Selected Date
st.subheader(f"Schedule for {selected_date.strftime('%B %d, %Y')}")
tasks = database.get_tasks_by_date(selected_date_str)

# Filters
filter_c1, filter_c2 = st.columns(2)
with filter_c1:
    filter_cat = st.multiselect(
        "Filter by Category",
        options=["Semester Study", "Revision", "Practice Test", "Python Coding", "DSA Practice", "Project Work"]
    )
with filter_c2:
    filter_sub = st.multiselect(
        "Filter by Subject",
        options=[s["code"] for s in subjects]
    )

filtered_tasks = tasks
if filter_cat:
    filtered_tasks = [t for t in filtered_tasks if t["category"] in filter_cat]
if filter_sub:
    filtered_tasks = [t for t in filtered_tasks if t.get("subject_code") in filter_sub]

if filtered_tasks:
    for t in filtered_tasks:
        col_check, col_info, col_actions = st.columns([1, 6, 2])
        is_done = bool(t["completed"])
        
        with col_check:
            new_done = st.checkbox("Done", value=is_done, key=f"chk_{t['id']}")
            if new_done != is_done:
                database.toggle_task_completion(t["id"], new_done)
                st.rerun()

        with col_info:
            strike = "text-decoration: line-through; opacity: 0.6;" if is_done else ""
            pri_color = "#ef4444" if t["priority"] == "High" else "#f59e0b" if t["priority"] == "Medium" else "#38bdf8"
            render_html(f"""
<div style="{strike}">
<strong style="font-size: 1rem; color: #f8fafc;">{t['title']}</strong>
<div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">
📂 {t['category']} • 🏷️ {t.get('subject_code', 'General')} • ⏱️ {t['planned_minutes']} mins • 
<span style="color: {pri_color}; font-weight: 600;">Priority: {t['priority']}</span>
</div>
</div>
""")

        with col_actions:
            act_col1, act_col2 = st.columns(2)
            with act_col1:
                with st.popover("✏️ Edit"):
                    e_title = st.text_input("Title", value=t["title"], key=f"e_title_{t['id']}")
                    e_cat = st.selectbox("Category", ["Semester Study", "Revision", "Practice Test", "Python Coding", "DSA Practice", "Project Work"], index=["Semester Study", "Revision", "Practice Test", "Python Coding", "DSA Practice", "Project Work"].index(t["category"]), key=f"e_cat_{t['id']}")
                    e_min = st.number_input("Minutes", value=t["planned_minutes"], step=15, key=f"e_min_{t['id']}")
                    e_pri = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(t["priority"]), key=f"e_pri_{t['id']}")
                    if st.button("Save", key=f"btn_save_{t['id']}"):
                        database.update_task(t["id"], t["task_date"], e_title, e_cat, t["subject_id"], e_min, e_pri)
                        st.rerun()
            with act_col2:
                if st.button("🗑️", key=f"del_{t['id']}", help="Delete task"):
                    database.delete_task(t["id"])
                    st.rerun()
        st.markdown("<hr style='border-color: #1e293b; margin: 8px 0;'>", unsafe_allow_html=True)
else:
    render_empty_state("No tasks match the selected filters or date.", "Use the form above to add tasks.")

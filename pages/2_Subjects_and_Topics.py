"""
pages/2_Subjects_and_Topics.py - Syllabus hierarchy, topic completion, and confidence tracking.
"""

import streamlit as st
from datetime import date
import database
import analytics
from components.theme import inject_focus_theme
from components.sidebar import render_sidebar
from components.metrics import render_header, render_metric_card, render_empty_state

st.set_page_config(page_title="Subjects & Topics | Study Analyzer", page_icon="📖", layout="wide")
database.init_db()
inject_focus_theme()
render_sidebar()

render_header("Subjects & Topics", "Track your syllabus progress, update module topic statuses, and rate your confidence.")

# Tab 1: Syllabus Tracking | Tab 2: Manage Subjects & Exam Dates | Tab 3: Add Custom Topics
tab1, tab2, tab3 = st.tabs(["📚 Syllabus & Topic Tracker", "⚙️ Manage Subjects & Exam Dates", "➕ Add Topics"])

subjects = database.get_all_subjects()
if not subjects:
    st.warning("No subjects found. Please add subjects in the 'Manage Subjects' tab.")

with tab1:
    if subjects:
        # Subject Selector
        subj_options = {s["id"]: f"{s['code']} - {s['name']}" for s in subjects}
        selected_subj_id = st.selectbox(
            "Select Subject to View / Update",
            options=list(subj_options.keys()),
            format_func=lambda x: subj_options[x]
        )
        
        current_subj = database.get_subject_by_id(selected_subj_id)
        topics = database.get_topics_by_subject(selected_subj_id)
        
        # Subject Overview Metrics
        tot_topics = len(topics)
        comp_topics = sum(1 for t in topics if t["status"] == "Completed")
        in_prog_topics = sum(1 for t in topics if t["status"] == "In Progress")
        rev_topics = sum(1 for t in topics if t["status"] == "Needs Revision")
        pct = (comp_topics / tot_topics * 100.0) if tot_topics > 0 else 0.0
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Completion", f"{round(pct, 1)}%", f"{comp_topics} of {tot_topics} topics done", color="#34d399")
        with m2:
            render_metric_card("In Progress", str(in_prog_topics), "Topics currently studying", color="#38bdf8")
        with m3:
            render_metric_card("Needs Revision", str(rev_topics), "Flagged for second review", color="#ef4444" if rev_topics > 0 else "#64748b")
        with m4:
            render_metric_card("Target Hours", f"{current_subj['target_hours']}h", f"Exam Date: {current_subj['exam_date']}", color="#f59e0b")

        st.progress(pct / 100.0)

        if tot_topics == 0:
            render_empty_state("No topics recorded for this subject.", "Use the 'Add Topics' tab above to populate syllabus units.")
        else:
            # Filters
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                all_units = sorted(list(set(t["unit_name"] for t in topics)))
                sel_unit = st.selectbox("Filter by Unit / Module", ["All Units"] + all_units)
            with f_col2:
                sel_status = st.selectbox("Filter by Status", ["All Statuses", "Not Started", "In Progress", "Completed", "Needs Revision"])

            filtered_topics = topics
            if sel_unit != "All Units":
                filtered_topics = [t for t in filtered_topics if t["unit_name"] == sel_unit]
            if sel_status != "All Statuses":
                filtered_topics = [t for t in filtered_topics if t["status"] == sel_status]

            # Group topics by unit for clean display
            units_in_view = sorted(list(set(t["unit_name"] for t in filtered_topics)))
            for u_name in units_in_view:
                unit_topics = [t for t in filtered_topics if t["unit_name"] == u_name]
                unit_done = sum(1 for t in unit_topics if t["status"] == "Completed")
                unit_pct = round(unit_done / len(unit_topics) * 100, 1)

                with st.expander(f"📌 {u_name} ({unit_done}/{len(unit_topics)} completed - {unit_pct}%)", expanded=True):
                    for t in unit_topics:
                        t_c1, t_c2, t_c3, t_c4 = st.columns([4, 2, 2, 1])
                        with t_c1:
                            st.markdown(f"**{t['topic_name']}**")
                        with t_c2:
                            # Status Dropdown
                            status_opts = ["Not Started", "In Progress", "Completed", "Needs Revision"]
                            new_status = st.selectbox(
                                "Status",
                                status_opts,
                                index=status_opts.index(t["status"]),
                                key=f"status_{t['id']}",
                                label_visibility="collapsed"
                            )
                        with t_c3:
                            # Confidence Rating
                            new_conf = st.slider(
                                "Confidence (1-5)",
                                min_value=1,
                                max_value=5,
                                value=t["confidence"],
                                key=f"conf_{t['id']}",
                                label_visibility="collapsed"
                            )
                        with t_c4:
                            # Quick Save or Delete
                            if st.button("💾", key=f"save_top_{t['id']}", help="Update status"):
                                database.update_topic_status(t["id"], new_status, new_conf)
                                st.rerun()

                        # Check if changed to auto-persist
                        if new_status != t["status"] or new_conf != t["confidence"]:
                            database.update_topic_status(t["id"], new_status, new_conf)
                            st.rerun()
                        st.markdown("<hr style='border-color: #33415522; margin: 4px 0;'>", unsafe_allow_html=True)

with tab2:
    st.markdown("### Manage Subjects & Examination Schedule")
    st.caption("Customize subject names, VTU course codes, target study hours, and exam dates (Nov 17–30, 2026).")
    
    for s in subjects:
        with st.expander(f"📘 {s['code']} - {s['name']}", expanded=False):
            with st.form(f"edit_subj_{s['id']}"):
                e_c1, e_c2 = st.columns(2)
                with e_c1:
                    e_code = st.text_input("Course Code", value=s["code"])
                    e_name = st.text_input("Subject Name", value=s["name"])
                with e_c2:
                    current_d = date.fromisoformat(s["exam_date"]) if s["exam_date"] else date.today()
                    e_exam = st.date_input("Exam Date", value=current_d)
                    e_target = st.number_input("Target Hours", min_value=5.0, max_value=200.0, value=float(s["target_hours"]), step=5.0)

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    save_subj = st.form_submit_button("Update Subject Details")
                    if save_subj:
                        database.update_subject(s["id"], e_name, e_code, e_exam.isoformat(), e_target)
                        st.success("Subject details updated!")
                        st.rerun()

            # Delete Subject Button with confirmation
            with st.popover("⚠️ Delete Subject"):
                st.write(f"Are you sure you want to delete **{s['code']} - {s['name']}** and all its associated topics?")
                if st.button("Yes, Delete Subject Permanently", key=f"del_subj_{s['id']}", type="primary"):
                    database.delete_subject(s["id"])
                    st.success("Subject removed.")
                    st.rerun()

    st.markdown("---")
    st.markdown("#### ➕ Add a New Subject")
    with st.form("add_new_subject_form", clear_on_submit=True):
        a_c1, a_c2 = st.columns(2)
        with a_c1:
            new_code = st.text_input("Course Code", placeholder="e.g. BCS704")
            new_name = st.text_input("Subject Name", placeholder="e.g. Cloud Computing")
        with a_c2:
            new_exam_date = st.date_input("Examination Date", value=date(2026, 11, 25))
            new_target_hrs = st.number_input("Target Study Hours", min_value=5.0, max_value=200.0, value=40.0, step=5.0)
        
        if st.form_submit_button("Create Subject", use_container_width=True):
            if not new_name.strip() or not new_code.strip():
                st.error("Course code and subject name are required.")
            else:
                database.add_subject(new_name, new_code, new_exam_date.isoformat(), new_target_hrs)
                st.success("Subject created!")
                st.rerun()

with tab3:
    st.markdown("### Add Custom Topics to Syllabus")
    if subjects:
        with st.form("add_topic_form", clear_on_submit=True):
            sub_id = st.selectbox(
                "Subject",
                options=[s["id"] for s in subjects],
                format_func=lambda x: next((f"{s['code']} - {s['name']}" for s in subjects if s["id"] == x), "")
            )
            unit_name = st.text_input("Unit / Module Name", placeholder="e.g. Module 3: Network Security Protocols")
            topic_name = st.text_input("Topic Name", placeholder="e.g. IPsec Architecture and ESP Protocol")
            
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                init_status = st.selectbox("Initial Status", ["Not Started", "In Progress", "Completed", "Needs Revision"])
            with t_col2:
                init_conf = st.slider("Initial Confidence", min_value=1, max_value=5, value=3)

            if st.form_submit_button("Add Topic to Syllabus", use_container_width=True):
                if not unit_name.strip() or not topic_name.strip():
                    st.error("Both unit name and topic name are required.")
                else:
                    database.add_topic(sub_id, unit_name, topic_name, init_status, init_conf)
                    st.success("Topic added successfully!")
                    st.rerun()
    else:
        st.info("Add subjects first to create topics.")

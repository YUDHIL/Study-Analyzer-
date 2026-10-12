"""
pages/5_Python_Practice.py - Python problem solving, independent solve rate, and concept tracking.
"""

import streamlit as st
from datetime import date
import database
import analytics
from components.theme import inject_focus_theme
from components.sidebar import render_sidebar
from components.metrics import render_header, render_metric_card, render_empty_state
from components.charts import create_coding_concepts_chart

st.set_page_config(page_title="Python Practice | Study Analyzer", page_icon="🐍", layout="wide")
database.init_db()
inject_focus_theme()
render_sidebar()

render_header("Python Practice Tracker", "Improve independent coding problem-solving skills, log hints used, and track concept mastery.")

coding_metrics = analytics.calculate_coding_metrics()

# Summary Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Attempted", str(coding_metrics["total_attempted"]), "Problems attempted", color="#38bdf8")
with m2:
    sol_pct = round((coding_metrics["total_solved"] / coding_metrics["total_attempted"] * 100), 1) if coding_metrics["total_attempted"] > 0 else 0.0
    render_metric_card("Total Solved", str(coding_metrics["total_solved"]), f"{sol_pct}% solve rate", color="#34d399")
with m3:
    render_metric_card("Independently Solved", str(coding_metrics["total_independent"]), "Solved without solutions", badge="No Hints", color="#2dd4bf")
with m4:
    rate = coding_metrics["independent_solve_rate"]
    badge_col = "#34d399" if rate >= 70 else "#f59e0b" if rate >= 40 else "#ef4444"
    render_metric_card("Independent Rate", f"{rate}%", "Indep. Solved / Attempted", color=badge_col)

st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

# Form to Log Coding Problem
with st.expander("💻 Log a Problem Solved / Attempted", expanded=coding_metrics["total_attempted"] == 0):
    with st.form("log_coding_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            p_name = st.text_input("Problem Title", placeholder="e.g. Two Sum, Valid Anagram, Reverse Linked List")
        with c2:
            p_concept = st.selectbox(
                "Core Concept",
                ["Strings", "Arrays / Lists", "Loops & Logic", "Dictionaries & HashMaps", "Functions & Scope", "Recursion", "OOP", "Binary Search", "Trees / Graphs", "Dynamic Programming", "General"]
            )
        with c3:
            p_platform = st.selectbox(
                "Platform",
                ["LeetCode", "HackerRank", "CodeChef", "GeeksforGeeks", "NeetCode", "College Lab", "Personal Practice"]
            )

        c4, c5, c6 = st.columns([1, 1, 1])
        with c4:
            p_date = st.date_input("Practice Date", value=date.today())
        with c5:
            p_mins = st.number_input("Time Spent (Minutes)", min_value=5, max_value=300, value=30, step=5)
        with c6:
            st.write("")
            st.write("")
            is_attempted = st.checkbox("Attempted Problem", value=True)

        c7, c8, c9 = st.columns(3)
        with c7:
            is_solved = st.checkbox("Solved Successfully")
        with c8:
            is_independent = st.checkbox("Solved Independently (Zero Solution Lookups)")
        with c9:
            used_hints = st.checkbox("Hints or Editorial Consulted")

        p_notes = st.text_area("Key Algorithmic Technique / Edge Cases Discovered", placeholder="e.g. Used two-pointer approach to achieve O(N) time and O(1) space...")

        submit_code = st.form_submit_button("Record Coding Session", use_container_width=True)
        if submit_code:
            if not p_name.strip():
                st.error("Problem title cannot be empty.")
            else:
                # If not solved, independent cannot be True
                final_ind = is_independent and is_solved
                database.add_coding_log(
                    practice_date=p_date.isoformat(),
                    problem_name=p_name,
                    concept=p_concept,
                    platform=p_platform,
                    attempted=1 if is_attempted else 0,
                    solved=1 if is_solved else 0,
                    independent=1 if final_ind else 0,
                    hints_used=1 if used_hints else 0,
                    minutes=p_mins,
                    notes=p_notes
                )
                st.success(f"Recorded problem '{p_name}'!")
                st.rerun()

# Concept Progress Chart
if coding_metrics["concept_breakdown"]:
    st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    st.plotly_chart(create_coding_concepts_chart(coding_metrics["concept_breakdown"]), use_container_width=True)

# Re-attempt Recommendations Panel
needs_re = coding_metrics.get("needs_reattempt", [])
if needs_re:
    st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    with st.expander(f"🔁 Problems Requiring Another Attempt ({len(needs_re)} problems where hints were used)", expanded=True):
        st.caption("To solidify your coding intuition, solve these problems from scratch without opening the solution:")
        for nr in needs_re[:6]:
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**{nr['problem_name']}** ({nr['platform']})")
                st.caption(f"Concept: {nr['concept']} • Practiced on {nr['practice_date']}")
            with c2:
                status_label = "Solved with hints" if nr["hints_used"] else "Attempted but not solved"
                st.markdown(f"<span style='color: #f59e0b;'>⚠️ {status_label}</span>", unsafe_allow_html=True)
            with c3:
                if st.button("Mark Re-solved!", key=f"resolv_{nr['id']}"):
                    database.update_coding_log(
                        nr["id"], nr["practice_date"], nr["problem_name"], nr["concept"], nr["platform"],
                        1, 1, 1, 0, nr["minutes"], "Re-solved independently without hints!"
                    )
                    st.success("Updated to independently solved!")
                    st.rerun()

# Coding Practice Log History
st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
st.subheader("📜 Practice Log History")

logs = database.get_coding_logs()
if logs:
    for l in logs:
        c1, c2, c3, c4 = st.columns([2, 4, 2, 1])
        with c1:
            st.markdown(f"**{l['practice_date']}**")
            st.caption(f"{l['platform']} • {l['minutes']} mins")
        with c2:
            st.markdown(f"**{l['problem_name']}** (`{l['concept']}`)")
            if l["notes"]:
                st.caption(f"💡 {l['notes']}")
        with c3:
            ind_tag = "🎯 Independent" if l["independent"] else "👀 Used Solution/Hints" if l["hints_used"] else "❌ Unsolved"
            tag_col = "#34d399" if l["independent"] else "#f59e0b" if l["hints_used"] else "#ef4444"
            st.markdown(f"<span style='color: {tag_col}; font-weight: 600;'>{ind_tag}</span>", unsafe_allow_html=True)
        with c4:
            if st.button("🗑️", key=f"del_code_{l['id']}", help="Delete entry"):
                database.delete_coding_log(l["id"])
                st.rerun()
        st.markdown("<hr style='border-color: #1e293b; margin: 4px 0;'>", unsafe_allow_html=True)
else:
    render_empty_state("No coding problems logged yet.", "Add your practice problems using the form above.")

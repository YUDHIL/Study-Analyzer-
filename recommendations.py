"""
recommendations.py - Rule-Based Recommendation Engine for Study Analyzer.

Generates transparent, explainable, actionable recommendations based on
exam urgency, unfinished topics, weak topics, test performance, and coding stats.
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import analytics
import database


def generate_recommendations(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate prioritized recommendations with clear reasoning.
    
    Each item contains:
    - title: Brief headline
    - message: Actionable guidance explaining the reasoning
    - category: 'Exam Urgency' | 'Revision' | 'Performance' | 'Coding' | 'Planning'
    - priority: 'High' | 'Medium' | 'Low'
    - action_page: Streamlit page name for user convenience
    """
    recs: List[Dict[str, Any]] = []

    # 1. Check Data Presence
    subjects = database.get_all_subjects(db_path)
    if not subjects:
        recs.append({
            "title": "Add Semester Subjects",
            "message": "No subjects found. Begin by adding your semester courses and configuring their exam dates.",
            "category": "Planning",
            "priority": "High",
            "action_page": "2_Subjects_and_Topics"
        })
        return recs

    syllabus_data = analytics.calculate_syllabus_completion(db_path)
    exam_countdown = analytics.get_exam_countdown(db_path)
    weak_topics = analytics.get_weak_topics(min_confidence=2, db_path=db_path)
    study_hours = analytics.calculate_study_hours(db_path)
    test_metrics = analytics.calculate_test_metrics(db_path)
    coding_metrics = analytics.calculate_coding_metrics(db_path)
    overdue_tasks = database.get_overdue_tasks(db_path=db_path)

    # 2. Overdue Tasks Alert
    if overdue_tasks:
        count = len(overdue_tasks)
        high_pri = sum(1 for t in overdue_tasks if t["priority"] == "High")
        recs.append({
            "title": f"Resolve {count} Overdue Tasks",
            "message": f"You have {count} uncompleted task(s) from past dates ({high_pri} high priority). Reschedule or complete them to keep your plan accurate.",
            "category": "Planning",
            "priority": "High" if high_pri > 0 else "Medium",
            "action_page": "1_Daily_Planner"
        })

    # 3. Upcoming Exam Urgency & Incomplete Topics
    upcoming = exam_countdown.get("upcoming_exams", [])
    if upcoming:
        next_exam = upcoming[0]
        days = next_exam["days_remaining"]
        s_id = next_exam["id"]
        # Find completion stats for this subject
        subj_stats = next((sb for sb in syllabus_data["subjects_breakdown"] if sb["subject_id"] == s_id), None)
        if subj_stats:
            uncompleted = subj_stats["total_topics"] - subj_stats["completed_topics"]
            if days <= 14 and uncompleted > 0:
                recs.append({
                    "title": f"Prioritize {next_exam['name']} ({next_exam['code']})",
                    "message": (
                        f"Examination is in {days} day(s), but {uncompleted} topic(s) remain unfinished "
                        f"({subj_stats['completion_percentage']}% completed). Dedicate 90 minutes today to finish the next module topic."
                    ),
                    "category": "Exam Urgency",
                    "priority": "High",
                    "action_page": "2_Subjects_and_Topics"
                })
            elif days <= 30 and uncompleted > 5:
                recs.append({
                    "title": f"Pace Preparation for {next_exam['code']}",
                    "message": (
                        f"Exam scheduled in {days} days with {uncompleted} remaining topics. "
                        f"Aim to complete 1 topic every 2 days to finish syllabus before the revision period."
                    ),
                    "category": "Exam Urgency",
                    "priority": "Medium",
                    "action_page": "2_Subjects_and_Topics"
                })

    # 4. Weak / Revision Topics
    if weak_topics:
        rev_count = sum(1 for t in weak_topics if t["status"] == "Needs Revision")
        low_conf = sum(1 for t in weak_topics if t["confidence"] <= 2 and t["status"] != "Needs Revision")
        sample_topic = weak_topics[0]["topic_name"]
        sample_subj = weak_topics[0]["subject_code"]
        recs.append({
            "title": "Strengthen Topics Needing Revision",
            "message": (
                f"{len(weak_topics)} topic(s) need attention ({rev_count} marked revision, {low_conf} low confidence). "
                f"Review '{sample_topic}' ({sample_subj}) during today's revision session."
            ),
            "category": "Revision",
            "priority": "High" if rev_count > 0 else "Medium",
            "action_page": "2_Subjects_and_Topics"
        })

    # 5. Low Test Scores / Subject Imbalance
    if test_metrics["total_tests"] > 0:
        for sp in test_metrics["subject_performance"]:
            if sp["average_percentage"] < 60.0 and sp["test_count"] >= 1:
                recs.append({
                    "title": f"Review {sp['subject_code']} Test Concepts",
                    "message": (
                        f"Average test score in {sp['subject_name']} is {sp['average_percentage']}%. "
                        f"Analyze mistakes in past tests and schedule a concept revision session."
                    ),
                    "category": "Performance",
                    "priority": "High",
                    "action_page": "4_Test_Performance"
                })
                break  # Alert on lowest scoring subject
    else:
        recs.append({
            "title": "Log a Diagnostic Practice Test",
            "message": "No test scores recorded yet. Take and log a short topic test to establish baseline performance metrics.",
            "category": "Performance",
            "priority": "Low",
            "action_page": "4_Test_Performance"
        })

    # 6. Python Coding Practice Guidance
    if coding_metrics["total_attempted"] > 0:
        solve_rate = coding_metrics["independent_solve_rate"]
        needs_reattempt = coding_metrics.get("needs_reattempt", [])
        if solve_rate < 50.0 and coding_metrics["total_attempted"] >= 3:
            recs.append({
                "title": "Boost Independent Problem Solving",
                "message": (
                    f"Your independent solve rate is {solve_rate}%. You used hints or viewed solutions on several problems. "
                    f"Re-attempt {min(2, len(needs_reattempt))} previously solved problems without checking solutions."
                ),
                "category": "Coding",
                "priority": "High",
                "action_page": "5_Python_Practice"
            })
        elif len(needs_reattempt) > 0:
            p_name = needs_reattempt[0]["problem_name"]
            recs.append({
                "title": f"Re-solve '{p_name}' Independently",
                "message": f"You previously solved '{p_name}' with hints. Try coding the complete solution from scratch without looking at hints.",
                "category": "Coding",
                "priority": "Medium",
                "action_page": "5_Python_Practice"
            })
    else:
        recs.append({
            "title": "Start Daily Python Practice",
            "message": "No coding problems logged yet. Solve 1 beginner/intermediate problem today (e.g., string or list manipulation) to begin building your streak.",
            "category": "Coding",
            "priority": "Medium",
            "action_page": "5_Python_Practice"
        })

    # 7. Study Habit & Session Logging
    if study_hours["sessions_count"] == 0:
        recs.append({
            "title": "Log Your First Study Session",
            "message": "Track your study sessions to unlock daily analytics, consistency charts, and subject distribution graphs.",
            "category": "Planning",
            "priority": "Info",
            "action_page": "3_Study_Log"
        })

    # Sort recommendations by Priority: High -> Medium -> Low/Info
    priority_order = {"High": 1, "Medium": 2, "Low": 3, "Info": 4}
    recs.sort(key=lambda x: priority_order.get(x.get("priority", "Low"), 5))

    return recs

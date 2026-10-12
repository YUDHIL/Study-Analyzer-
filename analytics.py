"""
analytics.py - Data Analytics and Metric Calculations for Study Analyzer.

Implements well-defined, robust formulas for syllabus completion,
test performance, coding progress, study consistency, and comparative trends.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import database


# ==============================================================================
# SYLLABUS & TOPIC METRICS
# ==============================================================================

def calculate_syllabus_completion(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate syllabus completion overall and per-subject.
    Formula: Completed topics / Total topics * 100.
    """
    subjects = database.get_all_subjects(db_path)
    all_topics = database.get_all_topics(db_path)

    if not subjects:
        return {
            "overall_percentage": 0.0,
            "total_topics": 0,
            "completed_topics": 0,
            "in_progress_topics": 0,
            "needs_revision_topics": 0,
            "not_started_topics": 0,
            "subjects_breakdown": []
        }

    # Group topics by subject_id
    topics_by_subject: Dict[int, List[Dict[str, Any]]] = {s["id"]: [] for s in subjects}
    for t in all_topics:
        s_id = t["subject_id"]
        if s_id in topics_by_subject:
            topics_by_subject[s_id].append(t)

    total_topics_count = len(all_topics)
    completed_topics_count = sum(1 for t in all_topics if t["status"] == "Completed")
    in_progress_count = sum(1 for t in all_topics if t["status"] == "In Progress")
    needs_revision_count = sum(1 for t in all_topics if t["status"] == "Needs Revision")
    not_started_count = sum(1 for t in all_topics if t["status"] == "Not Started")

    overall_percentage = (completed_topics_count / total_topics_count * 100.0) if total_topics_count > 0 else 0.0

    breakdown = []
    for s in subjects:
        sub_topics = topics_by_subject.get(s["id"], [])
        sub_total = len(sub_topics)
        sub_completed = sum(1 for t in sub_topics if t["status"] == "Completed")
        sub_in_prog = sum(1 for t in sub_topics if t["status"] == "In Progress")
        sub_rev = sum(1 for t in sub_topics if t["status"] == "Needs Revision")
        sub_pct = (sub_completed / sub_total * 100.0) if sub_total > 0 else 0.0

        # Calculate average confidence for topics that have been started
        conf_scores = [t["confidence"] for t in sub_topics if t["status"] != "Not Started"]
        avg_conf = (sum(conf_scores) / len(conf_scores)) if conf_scores else 0.0

        breakdown.append({
            "subject_id": s["id"],
            "subject_name": s["name"],
            "subject_code": s["code"],
            "exam_date": s["exam_date"],
            "target_hours": s["target_hours"],
            "total_topics": sub_total,
            "completed_topics": sub_completed,
            "in_progress_topics": sub_in_prog,
            "needs_revision_topics": sub_rev,
            "completion_percentage": round(sub_pct, 1),
            "average_confidence": round(avg_conf, 1)
        })

    return {
        "overall_percentage": round(overall_percentage, 1),
        "total_topics": total_topics_count,
        "completed_topics": completed_topics_count,
        "in_progress_topics": in_progress_count,
        "needs_revision_topics": needs_revision_count,
        "not_started_topics": not_started_count,
        "subjects_breakdown": breakdown
    }


def get_weak_topics(min_confidence: int = 2, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return topics marked 'Needs Revision' or with confidence <= min_confidence."""
    all_topics = database.get_all_topics(db_path)
    weak = [
        t for t in all_topics
        if t["status"] == "Needs Revision" or (t["status"] != "Not Started" and t["confidence"] <= min_confidence)
    ]
    return weak


# ==============================================================================
# STUDY TIME METRICS
# ==============================================================================

def calculate_study_hours(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Calculate total study hours, subject breakdown, and recent daily totals."""
    logs = database.get_study_logs(db_path=db_path)
    if not logs:
        return {
            "total_hours": 0.0,
            "total_minutes": 0,
            "sessions_count": 0,
            "subject_hours": {},
            "daily_hours_last_7_days": {}
        }

    total_minutes = sum(l["minutes"] for l in logs)
    total_hours = round(total_minutes / 60.0, 1)

    # Subject breakdown
    subject_minutes: Dict[str, int] = {}
    for l in logs:
        s_name = l["subject_name"] or "General / Non-Academic"
        subject_minutes[s_name] = subject_minutes.get(s_name, 0) + l["minutes"]

    subject_hours = {s: round(m / 60.0, 1) for s, m in subject_minutes.items()}

    # Daily hours for last 7 days
    today = date.today()
    daily_hours_7d = {}
    for i in range(6, -1, -1):
        day_str = (today - timedelta(days=i)).isoformat()
        day_mins = sum(l["minutes"] for l in logs if l["study_date"] == day_str)
        daily_hours_7d[day_str] = round(day_mins / 60.0, 2)

    return {
        "total_hours": total_hours,
        "total_minutes": total_minutes,
        "sessions_count": len(logs),
        "subject_hours": subject_hours,
        "daily_hours_last_7_days": daily_hours_7d
    }


def calculate_study_consistency(start_date: str, end_date: str, target_daily_hours: float = 3.0,
                                db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Formula: Days meeting configured study target / Elapsed days in selected period * 100.
    Never treats future days as missed study days.
    """
    s_dt = datetime.fromisoformat(start_date).date()
    e_dt = datetime.fromisoformat(end_date).date()
    today = date.today()

    # Cap effective end date at today
    effective_end = min(e_dt, today)
    if s_dt > effective_end:
        return {"consistency_percentage": 0.0, "days_meeting_target": 0, "elapsed_days": 0}

    elapsed_days = (effective_end - s_dt).days + 1
    logs = database.get_study_logs(start_date=start_date, end_date=effective_end.isoformat(), db_path=db_path)

    # Aggregate by date
    daily_minutes: Dict[str, int] = {}
    for l in logs:
        d = l["study_date"]
        daily_minutes[d] = daily_minutes.get(d, 0) + l["minutes"]

    target_minutes = target_daily_hours * 60.0
    days_meeting_target = sum(1 for m in daily_minutes.values() if m >= target_minutes)

    consistency_pct = (days_meeting_target / elapsed_days * 100.0) if elapsed_days > 0 else 0.0

    return {
        "consistency_percentage": round(consistency_pct, 1),
        "days_meeting_target": days_meeting_target,
        "elapsed_days": elapsed_days,
        "target_daily_hours": target_daily_hours
    }


# ==============================================================================
# TEST PERFORMANCE METRICS
# ==============================================================================

def calculate_test_metrics(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate test percentages and distinguish between:
    - Average of test percentages
    - Weighted percentage: sum(score) / sum(max_score) * 100
    """
    results = database.get_test_results(db_path=db_path)
    if not results:
        return {
            "total_tests": 0,
            "average_percentage": 0.0,
            "weighted_percentage": 0.0,
            "subject_performance": [],
            "recent_tests": []
        }

    percentages = [(r["score"] / r["max_score"] * 100.0) for r in results if r["max_score"] > 0]
    total_score = sum(r["score"] for r in results)
    total_max = sum(r["max_score"] for r in results)

    avg_pct = (sum(percentages) / len(percentages)) if percentages else 0.0
    weighted_pct = (total_score / total_max * 100.0) if total_max > 0 else 0.0

    # Group by subject
    subjects = database.get_all_subjects(db_path)
    subj_map = {s["id"]: s for s in subjects}
    tests_by_subj: Dict[int, List[Dict[str, Any]]] = {}
    for r in results:
        s_id = r["subject_id"]
        tests_by_subj.setdefault(s_id, []).append(r)

    subj_perf = []
    for s_id, s_tests in tests_by_subj.items():
        s_info = subj_map.get(s_id, {"name": f"Subject {s_id}", "code": ""})
        s_pcts = [(t["score"] / t["max_score"] * 100.0) for t in s_tests if t["max_score"] > 0]
        s_avg = (sum(s_pcts) / len(s_pcts)) if s_pcts else 0.0
        s_tot_score = sum(t["score"] for t in s_tests)
        s_tot_max = sum(t["max_score"] for t in s_tests)
        s_weighted = (s_tot_score / s_tot_max * 100.0) if s_tot_max > 0 else 0.0

        subj_perf.append({
            "subject_id": s_id,
            "subject_name": s_info.get("name", "Unknown"),
            "subject_code": s_info.get("code", ""),
            "test_count": len(s_tests),
            "average_percentage": round(s_avg, 1),
            "weighted_percentage": round(s_weighted, 1)
        })

    # Sort by average percentage ascending to highlight lower scores
    subj_perf.sort(key=lambda x: x["average_percentage"])

    return {
        "total_tests": len(results),
        "average_percentage": round(avg_pct, 1),
        "weighted_percentage": round(weighted_pct, 1),
        "subject_performance": subj_perf,
        "recent_tests": results[:5]
    }


# ==============================================================================
# PYTHON CODING METRICS
# ==============================================================================

def calculate_coding_metrics(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate coding practice progress:
    - Attempted problems count
    - Solved problems count
    - Independently solved count
    - Independent solve rate: (independent / attempted) * 100
    - Concept-wise distribution
    """
    logs = database.get_coding_logs(db_path=db_path)
    if not logs:
        return {
            "total_attempted": 0,
            "total_solved": 0,
            "total_independent": 0,
            "independent_solve_rate": 0.0,
            "total_minutes": 0,
            "concept_breakdown": [],
            "needs_reattempt": []
        }

    total_attempted = sum(l["attempted"] for l in logs)
    total_solved = sum(l["solved"] for l in logs)
    total_independent = sum(l["independent"] for l in logs)
    total_mins = sum(l["minutes"] for l in logs)

    indep_rate = (total_independent / total_attempted * 100.0) if total_attempted > 0 else 0.0

    # Breakdown by concept
    concept_map: Dict[str, Dict[str, int]] = {}
    for l in logs:
        c = l["concept"] or "General"
        if c not in concept_map:
            concept_map[c] = {"attempted": 0, "solved": 0, "independent": 0, "minutes": 0}
        concept_map[c]["attempted"] += l["attempted"]
        concept_map[c]["solved"] += l["solved"]
        concept_map[c]["independent"] += l["independent"]
        concept_map[c]["minutes"] += l["minutes"]

    breakdown = []
    for concept_name, stats in concept_map.items():
        att = stats["attempted"]
        rate = (stats["independent"] / att * 100.0) if att > 0 else 0.0
        breakdown.append({
            "concept": concept_name,
            "attempted": att,
            "solved": stats["solved"],
            "independent": stats["independent"],
            "minutes": stats["minutes"],
            "independent_rate": round(rate, 1)
        })

    # Problems needing another attempt (attempted but not independent, or hints were used)
    needs_reattempt = [l for l in logs if l["attempted"] == 1 and (l["independent"] == 0 or l["hints_used"] == 1)]

    return {
        "total_attempted": total_attempted,
        "total_solved": total_solved,
        "total_independent": total_independent,
        "independent_solve_rate": round(indep_rate, 1),
        "total_minutes": total_mins,
        "concept_breakdown": breakdown,
        "needs_reattempt": needs_reattempt
    }


# ==============================================================================
# TASK & PLANNER METRICS
# ==============================================================================

def calculate_task_metrics(task_date: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Calculate task completion rate and planned vs actual minutes for a date or all time."""
    if task_date:
        tasks = database.get_tasks_by_date(task_date, db_path=db_path)
        study_logs = database.get_study_logs(start_date=task_date, end_date=task_date, db_path=db_path)
    else:
        tasks = database.get_all_tasks(db_path=db_path)
        study_logs = database.get_study_logs(db_path=db_path)

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["completed"] == 1)
    planned_minutes = sum(t["planned_minutes"] for t in tasks)
    actual_minutes = sum(l["minutes"] for l in study_logs)

    completion_rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": total_tasks - completed_tasks,
        "completion_rate": round(completion_rate, 1),
        "planned_minutes": planned_minutes,
        "actual_minutes": actual_minutes,
        "difference_minutes": actual_minutes - planned_minutes
    }


# ==============================================================================
# EXAM URGENCY & COUNTDOWN
# ==============================================================================

def get_exam_countdown(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Calculate countdown to exams and order subjects by urgency."""
    subjects = database.get_all_subjects(db_path)
    today = date.today()

    upcoming = []
    past = []

    for s in subjects:
        if s["exam_date"]:
            try:
                ex_date = datetime.fromisoformat(s["exam_date"]).date()
                days_left = (ex_date - today).days
                item = {
                    "id": s["id"],
                    "name": s["name"],
                    "code": s["code"],
                    "exam_date": s["exam_date"],
                    "days_remaining": days_left,
                    "is_past": days_left < 0
                }
                if days_left >= 0:
                    upcoming.append(item)
                else:
                    past.append(item)
            except ValueError:
                continue

    upcoming.sort(key=lambda x: x["days_remaining"])

    next_exam = upcoming[0] if upcoming else None
    days_to_next = next_exam["days_remaining"] if next_exam else None

    return {
        "next_exam": next_exam,
        "days_to_next": days_to_next,
        "upcoming_exams": upcoming,
        "past_exams": past
    }


# ==============================================================================
# WEEKLY REPORT & COMPARISON
# ==============================================================================

def get_weekly_analytics_report(start_date: str, end_date: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Produce a 7-day analytics report and compare with the preceding 7-day period.
    Handles empty previous data safely without division by zero.
    """
    s_dt = datetime.fromisoformat(start_date).date()
    e_dt = datetime.fromisoformat(end_date).date()
    duration_days = (e_dt - s_dt).days + 1

    # Current period logs
    curr_logs = database.get_study_logs(start_date=start_date, end_date=end_date, db_path=db_path)
    curr_mins = sum(l["minutes"] for l in curr_logs)
    curr_hours = round(curr_mins / 60.0, 1)

    # Previous period of equal duration
    prev_e_dt = s_dt - timedelta(days=1)
    prev_s_dt = prev_e_dt - timedelta(days=duration_days - 1)
    prev_logs = database.get_study_logs(start_date=prev_s_dt.isoformat(), end_date=prev_e_dt.isoformat(), db_path=db_path)
    prev_mins = sum(l["minutes"] for l in prev_logs)
    prev_hours = round(prev_mins / 60.0, 1)

    hours_delta = round(curr_hours - prev_hours, 1)
    # Safe percentage delta
    if prev_hours > 0:
        hours_pct_change = round((hours_delta / prev_hours) * 100.0, 1)
    else:
        hours_pct_change = None  # Previous period had 0 activity; avoid misleading percentage

    # Subject distribution in current period
    subject_time: Dict[str, int] = {}
    for l in curr_logs:
        s_name = l["subject_name"] or "General"
        subject_time[s_name] = subject_time.get(s_name, 0) + l["minutes"]

    subject_dist = [{"subject": k, "hours": round(v / 60.0, 1)} for k, v in subject_time.items()]

    # Coding in current period
    coding_logs = database.get_coding_logs(db_path=db_path)
    curr_coding = [c for c in coding_logs if start_date <= c["practice_date"] <= end_date]
    prev_coding = [c for c in coding_logs if prev_s_dt.isoformat() <= c["practice_date"] <= prev_e_dt.isoformat()]

    coding_att_curr = sum(c["attempted"] for c in curr_coding)
    coding_sol_curr = sum(c["solved"] for c in curr_coding)
    coding_ind_curr = sum(c["independent"] for c in curr_coding)

    # Tasks in current period
    all_tasks = database.get_all_tasks(db_path=db_path)
    curr_tasks = [t for t in all_tasks if start_date <= t["task_date"] <= end_date]
    curr_tasks_tot = len(curr_tasks)
    curr_tasks_comp = sum(1 for t in curr_tasks if t["completed"] == 1)
    task_comp_rate = (curr_tasks_comp / curr_tasks_tot * 100.0) if curr_tasks_tot > 0 else 0.0

    return {
        "period": f"{start_date} to {end_date}",
        "current_hours": curr_hours,
        "previous_hours": prev_hours,
        "hours_delta": hours_delta,
        "hours_pct_change": hours_pct_change,
        "current_sessions": len(curr_logs),
        "subject_distribution": subject_dist,
        "coding_attempted": coding_att_curr,
        "coding_solved": coding_sol_curr,
        "coding_independent": coding_ind_curr,
        "tasks_total": curr_tasks_tot,
        "tasks_completed": curr_tasks_comp,
        "task_completion_rate": round(task_comp_rate, 1)
    }

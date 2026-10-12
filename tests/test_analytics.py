"""
tests/test_analytics.py - Automated tests for analytics calculations, edge cases, and recommendations.
"""

import os
import tempfile
from datetime import date, timedelta
import pytest
import database
import analytics
import recommendations


@pytest.fixture
def temp_db():
    """Isolated database fixture."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_analytics.db")
    database.init_db(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


def test_syllabus_completion_calculation(temp_db):
    """Test syllabus percentage calculation: completed / total * 100."""
    initial = analytics.calculate_syllabus_completion(temp_db)
    assert initial["overall_percentage"] == 0.0
    assert initial["total_topics"] > 0

    topics = database.get_all_topics(temp_db)
    # Mark first 5 topics as Completed
    for t in topics[:5]:
        database.update_topic_status(t["id"], "Completed", db_path=temp_db)

    after = analytics.calculate_syllabus_completion(temp_db)
    expected_pct = round((5 / initial["total_topics"]) * 100.0, 1)
    assert after["overall_percentage"] == expected_pct
    assert after["completed_topics"] == 5


def test_test_metrics_average_vs_weighted(temp_db):
    """Test distinction between average of percentages and weighted overall percentage."""
    subjects = database.get_all_subjects(temp_db)
    s1 = subjects[0]["id"]
    s2 = subjects[1]["id"]

    # Test 1: 10 / 20 = 50%
    database.add_test_result("2026-10-01", s1, "Quiz 1", 10.0, 20.0, db_path=temp_db)
    # Test 2: 90 / 100 = 90%
    database.add_test_result("2026-10-02", s2, "Midterm", 90.0, 100.0, db_path=temp_db)

    metrics = analytics.calculate_test_metrics(temp_db)
    # Average of percentages: (50 + 90) / 2 = 70.0%
    assert metrics["average_percentage"] == 70.0

    # Weighted percentage: (10 + 90) / (20 + 100) = 100 / 120 = 83.3%
    assert metrics["weighted_percentage"] == 83.3


def test_coding_metrics_independent_solve_rate(temp_db):
    """Test independent solve rate: independent / attempted * 100."""
    # 0 attempts
    empty_res = analytics.calculate_coding_metrics(temp_db)
    assert empty_res["independent_solve_rate"] == 0.0

    # 4 attempts: 3 solved (2 independent, 1 with hints), 1 unsolved
    database.add_coding_log("2026-10-10", "P1", "Strings", "LeetCode", 1, 1, 1, 0, 20, db_path=temp_db)
    database.add_coding_log("2026-10-10", "P2", "Arrays / Lists", "LeetCode", 1, 1, 1, 0, 30, db_path=temp_db)
    database.add_coding_log("2026-10-11", "P3", "Recursion", "LeetCode", 1, 1, 0, 1, 45, db_path=temp_db)
    database.add_coding_log("2026-10-12", "P4", "Dynamic Programming", "LeetCode", 1, 0, 0, 1, 40, db_path=temp_db)

    metrics = analytics.calculate_coding_metrics(temp_db)
    assert metrics["total_attempted"] == 4
    assert metrics["total_solved"] == 3
    assert metrics["total_independent"] == 2
    # Rate = 2 / 4 * 100 = 50.0%
    assert metrics["independent_solve_rate"] == 50.0
    assert len(metrics["needs_reattempt"]) == 2  # P3 and P4


def test_task_metrics_and_planned_vs_actual(temp_db):
    """Test task completion rate and planned vs actual study time."""
    today = date.today().isoformat()
    database.add_task(today, "Task 1", "Semester Study", None, 60, "High", temp_db)
    t2 = database.add_task(today, "Task 2", "Revision", None, 60, "Medium", temp_db)
    database.toggle_task_completion(t2, True, temp_db)

    # Actual study: 90 mins
    database.add_study_log(today, None, "Topic A", 90, 4, "", temp_db)

    t_res = analytics.calculate_task_metrics(task_date=today, db_path=temp_db)
    assert t_res["total_tasks"] == 2
    assert t_res["completed_tasks"] == 1
    assert t_res["completion_rate"] == 50.0
    assert t_res["planned_minutes"] == 120
    assert t_res["actual_minutes"] == 90
    assert t_res["difference_minutes"] == -30


def test_recommendations_generation(temp_db):
    """Verify recommendation generation without errors and expected advice."""
    recs = recommendations.generate_recommendations(temp_db)
    assert len(recs) > 0
    # Every recommendation must have a title, message, category, priority
    for r in recs:
        assert "title" in r
        assert "message" in r
        assert "category" in r
        assert r["priority"] in ["High", "Medium", "Low", "Info"]

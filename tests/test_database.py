"""
tests/test_database.py - Automated tests for SQLite schema, CRUD operations, and constraints.
"""

import os
import tempfile
import pytest
import database


@pytest.fixture
def temp_db():
    """Fixture providing an isolated temporary database path for each test."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_study.db")
    database.init_db(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


def test_db_initialization_and_seeding(temp_db):
    """Verify that init_db creates all 5 subjects and their 5 modules/topics."""
    subjects = database.get_all_subjects(temp_db)
    assert len(subjects) == 5
    codes = [s["code"] for s in subjects]
    assert "BCS701" in codes
    assert "BCS702" in codes
    assert "BCS703" in codes
    assert "BCS714D" in codes
    assert "BME755D" in codes

    topics = database.get_all_topics(temp_db)
    assert len(topics) >= 25  # 5 subjects * 5 modules minimum


def test_subject_crud(temp_db):
    """Test creating, reading, updating, and deleting subjects."""
    subj_id = database.add_subject("Machine Learning", "BCS705", "2026-11-28", 45.0, db_path=temp_db)
    subj = database.get_subject_by_id(subj_id, temp_db)
    assert subj is not None
    assert subj["name"] == "Machine Learning"
    assert subj["code"] == "BCS705"
    assert subj["target_hours"] == 45.0

    # Update
    updated = database.update_subject(subj_id, "Advanced Machine Learning", "BCS705", "2026-11-29", 50.0, db_path=temp_db)
    assert updated is True
    subj_after = database.get_subject_by_id(subj_id, temp_db)
    assert subj_after["name"] == "Advanced Machine Learning"
    assert subj_after["target_hours"] == 50.0

    # Delete
    deleted = database.delete_subject(subj_id, temp_db)
    assert deleted is True
    assert database.get_subject_by_id(subj_id, temp_db) is None


def test_topic_status_and_confidence(temp_db):
    """Test updating topic status and confidence rating."""
    topics = database.get_all_topics(temp_db)
    assert len(topics) > 0
    t = topics[0]

    # Update status to Completed and confidence to 5
    ok = database.update_topic_status(t["id"], "Completed", confidence=5, db_path=temp_db)
    assert ok is True

    updated_topics = database.get_all_topics(temp_db)
    t_after = next(x for x in updated_topics if x["id"] == t["id"])
    assert t_after["status"] == "Completed"
    assert t_after["confidence"] == 5


def test_task_crud_and_toggle(temp_db):
    """Test adding tasks, toggling completion, and overdue queries."""
    task_id = database.add_task(
        task_date="2026-10-10",
        title="Review IoT Module 1",
        category="Semester Study",
        subject_id=None,
        planned_minutes=90,
        priority="High",
        db_path=temp_db
    )
    assert task_id > 0

    tasks = database.get_tasks_by_date("2026-10-10", temp_db)
    assert len(tasks) == 1
    assert tasks[0]["completed"] == 0

    # Toggle completion
    database.toggle_task_completion(task_id, True, temp_db)
    tasks_done = database.get_tasks_by_date("2026-10-10", temp_db)
    assert tasks_done[0]["completed"] == 1
    assert tasks_done[0]["completed_at"] is not None


def test_study_log_validation(temp_db):
    """Test study log insertion and negative duration validation."""
    log_id = database.add_study_log(
        study_date="2026-10-12",
        subject_id=None,
        topic="CUDA Thread Hierarchies",
        minutes=60,
        understanding=4,
        notes="Understood blocks and grids",
        db_path=temp_db
    )
    assert log_id > 0

    # Invalid negative duration
    with pytest.raises(ValueError, match="positive"):
        database.add_study_log("2026-10-12", None, "Invalid", -15, db_path=temp_db)


def test_test_results_validation(temp_db):
    """Test score validation (score <= max_score > 0)."""
    subjects = database.get_all_subjects(temp_db)
    s_id = subjects[0]["id"]

    t_id = database.add_test_result(
        test_date="2026-10-12",
        subject_id=s_id,
        test_name="Quiz 1",
        score=22.5,
        max_score=25.0,
        notes="Good performance",
        db_path=temp_db
    )
    assert t_id > 0

    # Score exceeding max_score
    with pytest.raises(ValueError, match="between 0 and maximum"):
        database.add_test_result("2026-10-12", s_id, "Bad Quiz", 30.0, 25.0, db_path=temp_db)

    # Non-positive max_score
    with pytest.raises(ValueError, match="positive"):
        database.add_test_result("2026-10-12", s_id, "Bad Max", 5.0, 0.0, db_path=temp_db)


def test_coding_log_independent_constraint(temp_db):
    """Test that unsolved problems cannot be marked independent."""
    # Attempted and solved independently
    c1 = database.add_coding_log(
        practice_date="2026-10-12",
        problem_name="Two Sum",
        concept="Arrays / Lists",
        platform="LeetCode",
        attempted=1,
        solved=1,
        independent=1,
        hints_used=0,
        minutes=25,
        db_path=temp_db
    )
    logs = database.get_coding_logs(db_path=temp_db)
    assert logs[0]["independent"] == 1

    # Attempted, NOT solved, but independent flag requested -> must resolve to 0
    c2 = database.add_coding_log(
        practice_date="2026-10-12",
        problem_name="Hard DP",
        concept="Dynamic Programming",
        platform="LeetCode",
        attempted=1,
        solved=0,
        independent=1,
        hints_used=1,
        minutes=45,
        db_path=temp_db
    )
    logs = database.get_coding_logs(db_path=temp_db)
    unsolved = next(l for l in logs if l["id"] == c2)
    assert unsolved["independent"] == 0

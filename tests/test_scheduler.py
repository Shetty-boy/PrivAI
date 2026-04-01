"""
Tests for task scheduler / manager.
"""
import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.database import SessionLocal, Task, init_db
from app.tools.scheduler import create_task, delete_task, get_all_tasks, update_task, update_task_status


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    yield
    db = SessionLocal()
    db.query(Task).delete()
    db.commit()
    db.close()


def _create_test_task(task_name="Test Task", priority="medium"):
    db = SessionLocal()
    task = Task(task=task_name, priority=priority, status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()
    return task_id


def test_get_all_tasks_empty():
    tasks = get_all_tasks()
    assert isinstance(tasks, list)
    assert len(tasks) == 0


def test_get_all_tasks_returns_task():
    _create_test_task("Write unit tests")
    tasks = get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0]["task"] == "Write unit tests"
    assert tasks[0]["status"] == "pending"


def test_update_task_status():
    task_id = _create_test_task()
    update_task_status(task_id, "done")
    tasks = get_all_tasks()
    assert tasks[0]["status"] == "done"


def test_update_task_fields():
    task_id = _create_test_task("Original Task")
    updated = update_task(task_id, {
        "task": "Updated Task",
        "due_date": "2026-04-06",
        "due_time": "17:00",
        "priority": "high",
    })
    assert updated["task"] == "Updated Task"
    assert updated["due_date"] == "2026-04-06"
    assert updated["due_time"] == "17:00"
    assert updated["priority"] == "high"


def test_delete_task():
    task_id = _create_test_task("Task to delete")
    delete_task(task_id)
    tasks = get_all_tasks()
    assert len(tasks) == 0


@patch("app.tools.scheduler.chat")
def test_create_task_from_nlp(mock_chat):
    mock_chat.return_value = '{"task": "Submit assignment", "due_date": "2026-04-04", "due_time": "17:00", "priority": "high"}'
    result = create_task("Submit assignment by Friday 5pm urgent")
    assert result["task"] == "Submit assignment"
    assert result["due_date"] == "2026-04-04"
    assert result["priority"] == "high"


@patch("app.tools.scheduler.chat")
def test_create_task_handles_bad_json(mock_chat):
    mock_chat.return_value = "I cannot parse this."
    result = create_task("Buy groceries tomorrow")
    assert "task" in result
    assert result["due_date"] is not None


@patch("app.tools.scheduler.chat")
def test_create_task_parses_weekday_from_message(mock_chat):
    mock_chat.return_value = '{"task": "Submit report", "due_date": null, "due_time": null, "priority": "medium"}'
    result = create_task("Submit report on Monday")
    assert result["due_date"] is not None


@patch("app.tools.scheduler.chat")
def test_create_task_parses_priority_from_message(mock_chat):
    mock_chat.return_value = '{"task": "Submit report", "due_date": null, "due_time": null, "priority": "medium"}'
    result = create_task("Submit report on Monday urgent")
    assert result["priority"] == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

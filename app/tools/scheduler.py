"""
Scheduler / Task Manager with deterministic cleanup for dates, times, and priority.
"""
import json
import re
from datetime import date, datetime, timedelta

from app.config import PRIMARY_MODEL
from app.models.llm_client import chat
from app.storage.database import SessionLocal, Task

TASK_PARSE_PROMPT = """Extract task information from the user's message and return valid JSON only.

User message: "{message}"

Return this exact JSON structure (no markdown, no explanation):
{{
  "task": "short task description",
  "due_date": "YYYY-MM-DD or null",
  "due_time": "HH:MM or null",
  "priority": "low or medium or high"
}}

Rules:
- due_date: parse relative terms like "tomorrow", "friday", "next week" into actual dates from today ({today})
- due_time: use 24hr format, null if not mentioned
- priority: "high" if urgent/important mentioned, "low" if casual, else "medium"
- task: be concise but descriptive"""

WEEKDAY_TO_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def create_task(natural_language: str) -> dict:
    """
    Parse natural language into a structured task and save to SQLite.
    """
    today = date.today().strftime("%Y-%m-%d")
    prompt = TASK_PARSE_PROMPT.format(message=natural_language, today=today)

    try:
        response = chat(prompt, model=PRIMARY_MODEL)
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            task_data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in LLM response")
    except (json.JSONDecodeError, ValueError):
        task_data = {
            "task": natural_language[:200],
            "due_date": None,
            "due_time": None,
            "priority": "medium",
        }

    task_data = _post_process_task_data(task_data, natural_language)

    db = SessionLocal()
    try:
        new_task = Task(
            task=task_data.get("task", natural_language[:200]),
            due_date=task_data.get("due_date"),
            due_time=task_data.get("due_time"),
            priority=task_data.get("priority", "medium"),
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        task_data["id"] = new_task.id
        return task_data
    finally:
        db.close()


def get_all_tasks(status: str = None) -> list[dict]:
    db = SessionLocal()
    try:
        query = db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        tasks = query.order_by(Task.created_at.desc()).all()
        return [_task_to_dict(task) for task in tasks]
    finally:
        db.close()


def update_task_status(task_id: int, status: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            db.commit()
    finally:
        db.close()


def update_task(task_id: int, updates: dict) -> dict | None:
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        if "task" in updates and updates["task"] is not None:
            task.task = updates["task"]
        if "due_date" in updates:
            task.due_date = updates["due_date"] or None
        if "due_time" in updates:
            task.due_time = updates["due_time"] or None
        if "priority" in updates and updates["priority"] in {"low", "medium", "high"}:
            task.priority = updates["priority"]
        if "status" in updates and updates["status"] in {"pending", "done"}:
            task.status = updates["status"]

        db.commit()
        db.refresh(task)
        return _task_to_dict(task)
    finally:
        db.close()


def delete_task(task_id: int):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
    finally:
        db.close()


def delete_task_by_name(message: str) -> str | None:
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.status == "pending").all()
        for task in tasks:
            if task.task.lower() in message.lower() or any(
                word in task.task.lower() for word in message.lower().split() if len(word) > 4
            ):
                name = task.task
                db.delete(task)
                db.commit()
                return name
        return None
    finally:
        db.close()


def _post_process_task_data(task_data: dict, natural_language: str) -> dict:
    message = natural_language.lower()
    cleaned = {
        "task": (task_data.get("task") or natural_language[:200]).strip(),
        "due_date": task_data.get("due_date"),
        "due_time": _normalize_time(task_data.get("due_time")),
        "priority": _normalize_priority(task_data.get("priority"), message),
    }

    parsed_due_date = _extract_due_date(message)
    if parsed_due_date:
        cleaned["due_date"] = parsed_due_date

    parsed_due_time = _extract_due_time(message)
    if parsed_due_time:
        cleaned["due_time"] = parsed_due_time

    return cleaned


def _normalize_priority(priority: str | None, message: str) -> str:
    if any(word in message for word in ["urgent", "asap", "important", "high priority", "critical"]):
        return "high"
    if any(word in message for word in ["low priority", "whenever", "not urgent", "later"]):
        return "low"
    if priority in {"low", "medium", "high"}:
        return priority
    return "medium"


def _extract_due_date(message: str) -> str | None:
    today = date.today()

    if "today" in message:
        return today.isoformat()
    if "tomorrow" in message:
        return (today + timedelta(days=1)).isoformat()
    if "next week" in message:
        return (today + timedelta(days=7)).isoformat()

    for weekday, target_index in WEEKDAY_TO_INDEX.items():
        if weekday in message:
            days_ahead = (target_index - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            if f"next {weekday}" in message:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).isoformat()

    iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", message)
    if iso_match:
        return iso_match.group(1)
    return None


def _extract_due_time(message: str) -> str | None:
    am_pm_match = re.search(r"\b(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", message)
    if am_pm_match:
        hour = int(am_pm_match.group(1))
        minute = int(am_pm_match.group(2) or "00")
        suffix = am_pm_match.group(3)
        if suffix == "pm" and hour != 12:
            hour += 12
        if suffix == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute:02d}"

    twenty_four_match = re.search(r"\b(?:at\s*)?([01]?\d|2[0-3]):([0-5]\d)\b", message)
    if twenty_four_match:
        return f"{int(twenty_four_match.group(1)):02d}:{int(twenty_four_match.group(2)):02d}"
    return None


def _normalize_time(value: str | None) -> str | None:
    if not value:
        return None
    match = re.match(r"^(\d{1,2}):(\d{2})$", str(value).strip())
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return f"{hour:02d}:{minute:02d}"
    return None


def _task_to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "task": task.task,
        "due_date": task.due_date,
        "due_time": task.due_time,
        "priority": task.priority,
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }

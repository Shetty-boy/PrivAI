"""
Intent Detector — Classifies user input into one of the known intents.
Uses TinyLlama for fast classification.
"""
import re

from app.models.llm_client import chat_fast

# All supported intents
INTENTS = [
    "summarize",          # User wants to summarize a file/text
    "schedule",           # User wants to create a task or reminder
    "query_document",     # User wants to ask a question about their documents
    "list_tasks",         # User wants to see their task list
    "delete_task",        # User wants to delete a task
    "general_chat",       # Default: general conversation
]

INTENT_PROMPT_TEMPLATE = """You are an intent classifier for a personal AI assistant.
Classify the user's message into exactly ONE of these categories:
- summarize: user wants to summarize text, files, or notes
- schedule: user wants to create a task, reminder, or schedule something
- query_document: user wants to search or ask questions about their documents
- list_tasks: user wants to see their current tasks or to-do list
- delete_task: user wants to remove or complete a task
- general_chat: anything else, general conversation or questions

User message: "{message}"

Respond with only the category name. No explanation, no punctuation — just the exact word."""


def detect_intent(message: str) -> str:
    """
    Classify user input into one of the supported intents.

    Args:
        message: Raw user input string.

    Returns:
        One of the INTENTS strings.
    """
    try:
        fallback_intent = _keyword_fallback(message)
        if fallback_intent != "general_chat":
            return fallback_intent

        prompt = INTENT_PROMPT_TEMPLATE.format(message=message)
        result = chat_fast(prompt)
        parsed_intent = _parse_llm_intent(result)

        if parsed_intent and _intent_matches_message(parsed_intent, message):
            return parsed_intent

        # Fallback: keyword-based matching
        return fallback_intent

    except Exception:
        return _keyword_fallback(message)


def _keyword_fallback(message: str) -> str:
    """Rule-based fallback if LLM fails."""
    msg = message.lower()

    # Strong, explicit task-management commands should win first.
    if any(k in msg for k in ["delete task", "remove task", "done with", "complete task"]):
        return "delete_task"
    if any(k in msg for k in ["list tasks", "show tasks", "my tasks", "pending tasks", "to-do list"]):
        return "list_tasks"

    # Document search should only trigger when the user clearly references stored docs/notes/files.
    if any(k in msg for k in [
        "what does",
        "find in",
        "search",
        "according to",
        "in the document",
        "in my notes",
        "in my documents",
        "from my document",
        "from my notes",
        "project file",
        "uploaded file",
    ]):
        return "query_document"

    # Summarization should trigger only for explicit summary/file-summary asks.
    if any(k in msg for k in [
        "summarize",
        "summary",
        "sum up",
        "tldr",
        "condense",
        "shorten this",
        "summarise",
    ]):
        return "summarize"

    # Scheduling should be driven by reminder / due-date language rather than generic questions.
    if any(k in msg for k in [
        "remind",
        "schedule",
        "todo",
        "to do",
        "set a task",
        "set reminder",
        "deadline",
        "due ",
        "due tomorrow",
        "due today",
        "tomorrow",
        "next week",
        "at 5pm",
        "at 6pm",
        "by friday",
        "by monday",
    ]):
        return "schedule"

    # "task" on its own is too broad, but imperative reminders containing it are useful signals.
    if "task" in msg and any(k in msg for k in ["create", "add", "new", "remind"]):
        return "schedule"

    return "general_chat"


def _parse_llm_intent(raw_result: str) -> str | None:
    """
    Parse the classifier model response conservatively.

    We only trust the result when it resolves to exactly one supported intent.
    If the model rambles or lists multiple categories, we fall back to rules.
    """
    normalized = raw_result.strip().lower().replace("-", "_")
    normalized = re.sub(r"[^a-z_\n ]+", " ", normalized)

    matches = []
    for intent in INTENTS:
        pattern = rf"\b{re.escape(intent)}\b"
        if re.search(pattern, normalized):
            matches.append(intent)

    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]

    return None


def _intent_matches_message(intent: str, message: str) -> bool:
    """
    Validate whether a parsed intent is supported by the actual user wording.

    This prevents the classifier model from forcing tool-specific intents for
    broad questions like "What is machine learning?".
    """
    msg = message.lower()

    intent_signals = {
        "summarize": [
            "summarize", "summary", "sum up", "tldr", "condense", "summarise",
            "shorten this",
        ],
        "schedule": [
            "remind", "schedule", "todo", "to do", "deadline", "due ",
            "tomorrow", "next week", "by friday", "by monday", "at ",
        ],
        "query_document": [
            "document", "documents", "notes", "file", "pdf", "docx",
            "according to", "search", "find in", "uploaded",
        ],
        "list_tasks": [
            "list tasks", "show tasks", "my tasks", "to-do list", "pending tasks",
        ],
        "delete_task": [
            "delete task", "remove task", "complete task", "done with",
        ],
        "general_chat": [],
    }

    if intent == "general_chat":
        return True

    return any(signal in msg for signal in intent_signals.get(intent, []))

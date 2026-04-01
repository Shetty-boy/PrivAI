"""
Conversation Memory — Store and retrieve chat history using SQLite.
"""
from datetime import datetime
from app.storage.database import SessionLocal, ConversationMessage


def add_message(session_id: str, role: str, content: str):
    """Persist a single message to the conversation history."""
    db = SessionLocal()
    try:
        msg = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
        )
        db.add(msg)
        db.commit()
    finally:
        db.close()


def get_history(session_id: str, limit: int = 20) -> list[dict]:
    """
    Retrieve the most recent messages for a session.

    Returns:
        List of {role, content, timestamp} dicts in chronological order.
    """
    db = SessionLocal()
    try:
        msgs = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            }
            for m in reversed(msgs)
        ]
    finally:
        db.close()


def clear_history(session_id: str):
    """Delete all messages for a given session."""
    db = SessionLocal()
    try:
        db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).delete()
        db.commit()
    finally:
        db.close()


def get_all_sessions() -> list[str]:
    """Return list of unique session IDs."""
    db = SessionLocal()
    try:
        results = db.query(ConversationMessage.session_id).distinct().all()
        return [r[0] for r in results]
    finally:
        db.close()

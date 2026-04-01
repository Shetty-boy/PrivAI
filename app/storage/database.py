"""
Database Setup — SQLAlchemy + SQLite
Defines all table models and initializes the database.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.config import DB_PATH

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Table Models ─────────────────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String(500), nullable=False)
    due_date = Column(String(20), nullable=True)
    due_time = Column(String(10), nullable=True)
    priority = Column(String(10), default="medium")
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)   # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class IndexedDocument(Base):
    __tablename__ = "indexed_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(200), unique=True, nullable=False)
    filename = Column(String(300), nullable=False)
    filepath = Column(String(500), nullable=False)
    chunk_count = Column(Integer, default=0)
    indexed_at = Column(DateTime, default=datetime.utcnow)


# ─── Init ─────────────────────────────────────────────────────────────────────

def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI routes — yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

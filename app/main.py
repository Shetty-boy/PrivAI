"""
FastAPI main application entry point.
"""
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.intent_detector import detect_intent
from app.agents.task_planner import plan_and_execute
from app.config import API_HOST, API_PORT, DOCUMENTS_DIR
from app.memory.conversation import add_message, clear_history, get_history
from app.storage.database import init_db
from app.storage.file_manager import list_documents, save_uploaded_file
from app.tools.rag_engine import answer_query, index_document, list_indexed_documents
from app.tools.scheduler import create_task, delete_task, get_all_tasks, update_task, update_task_status
from app.tools.summarizer import summarize_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Database initialized")
    print("PAI Assistant backend ready")
    yield
    print("Backend shutting down")


app = FastAPI(
    title="Privacy-Preserving AI Assistant",
    description="Fully local AI assistant - no cloud, no data leakage",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    intent: str
    agent_name: str
    agent_display_name: str
    handoff_trace: list[dict]


class TaskRequest(BaseModel):
    text: str


class TaskUpdateRequest(BaseModel):
    task: str | None = None
    due_date: str | None = None
    due_time: str | None = None
    priority: str | None = None
    status: str | None = None


class QueryRequest(BaseModel):
    query: str
    doc_id: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "message": "PAI Assistant is running locally"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    intent = detect_intent(req.message)
    result = plan_and_execute(req.message, intent, session_id=req.session_id)
    add_message(req.session_id, role="user", content=req.message)
    add_message(req.session_id, role="assistant", content=result.reply)
    return ChatResponse(
        reply=result.reply,
        intent=intent,
        agent_name=result.agent_name,
        agent_display_name=result.agent_display_name,
        handoff_trace=[step.model_dump() for step in result.handoff_trace],
    )


@app.post("/summarize")
async def summarize(
    file: UploadFile = File(...),
    detail_level: str = Form("standard"),
    format_type: str = Form("structured"),
):
    saved_path = save_uploaded_file(file)
    try:
        result = summarize_file(
            saved_path,
            detail_level=detail_level,
            format_type=format_type,
        )
        return {
            "summary": result["summary"],
            "filename": file.filename,
            "chunk_count": result["chunk_count"],
            "time_seconds": result["time_seconds"],
            "detail_level": result["detail_level"],
            "format_type": result["format_type"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/tasks/create")
async def create_task_from_text(req: TaskRequest):
    return create_task(req.text)


@app.get("/tasks")
def get_tasks():
    return get_all_tasks()


@app.delete("/tasks/{task_id}")
def remove_task(task_id: int):
    delete_task(task_id)
    return {"message": "Task deleted"}


@app.patch("/tasks/{task_id}/done")
def mark_done(task_id: int):
    update_task_status(task_id, "done")
    return {"message": "Task marked as done"}


@app.patch("/tasks/{task_id}")
def edit_task(task_id: int, req: TaskUpdateRequest):
    updated = update_task(task_id, req.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    saved_path = save_uploaded_file(file)
    doc_id = os.path.splitext(file.filename)[0]
    index_document(saved_path, doc_id)
    return {"message": f"'{file.filename}' indexed successfully", "doc_id": doc_id}


@app.get("/documents")
def get_documents():
    return list_documents()


@app.post("/documents/query")
async def query_documents(req: QueryRequest):
    answer = answer_query(req.query)
    return {"answer": answer, "query": req.query}


@app.get("/documents/indexed")
def get_indexed():
    return list_indexed_documents()


@app.get("/history/{session_id}")
def get_chat_history(session_id: str):
    return get_history(session_id)


@app.delete("/history/{session_id}")
def clear_chat_history(session_id: str):
    clear_history(session_id)
    return {"message": "History cleared"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)

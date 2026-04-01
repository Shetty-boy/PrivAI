"""
RAG Engine — Retrieval Augmented Generation for document Q&A.
Index documents once, query them anytime — fully local.
"""
import os
from datetime import datetime
from app.memory.vector_store import add_chunks, search, get_all_doc_ids
from app.storage.file_manager import extract_text, chunk_text
from app.storage.database import SessionLocal, IndexedDocument
from app.models.llm_client import chat
from app.config import PRIMARY_MODEL, TOP_K_RESULTS

RAG_PROMPT = """You are a helpful assistant answering questions based strictly on the provided document context.
If the answer is not in the context, say "I couldn't find that information in the indexed documents."
Do NOT make up information. Be concise and factual.

Context from documents:
{context}

Question: {question}

Answer:"""


def index_document(filepath: str, doc_id: str) -> int:
    """
    Extract text from a file, create embeddings, and store in ChromaDB.
    Also records the document in SQLite for tracking.

    Args:
        filepath: Absolute path to the document.
        doc_id: Unique document identifier (typically filename without extension).

    Returns:
        Number of chunks indexed.
    """
    text = extract_text(filepath)
    chunks = chunk_text(text)

    chunk_count = add_chunks(doc_id, chunks)

    # Record in SQLite
    db = SessionLocal()
    try:
        existing = db.query(IndexedDocument).filter(IndexedDocument.doc_id == doc_id).first()
        if existing:
            existing.chunk_count = chunk_count
            existing.indexed_at = datetime.utcnow()
        else:
            record = IndexedDocument(
                doc_id=doc_id,
                filename=os.path.basename(filepath),
                filepath=filepath,
                chunk_count=chunk_count,
                indexed_at=datetime.utcnow(),
            )
            db.add(record)
        db.commit()
    finally:
        db.close()

    return chunk_count


def answer_query(query: str, model: str = PRIMARY_MODEL) -> str:
    """
    Answer a question using retrieved document chunks (RAG pipeline).

    Step 1: Embed query
    Step 2: Find top-K similar chunks in ChromaDB
    Step 3: Feed context + question to LLM
    Step 4: Return grounded answer

    Args:
        query: The user's question.
        model: LLM model to use for generation.

    Returns:
        Answer string.
    """
    results = search(query, top_k=TOP_K_RESULTS)

    if not results:
        return "No documents have been indexed yet. Please upload and index documents first."

    context_parts = []
    for r in results:
        context_parts.append(f"[From: {r['doc_id']}]\n{r['text']}")
    context = "\n\n".join(context_parts)

    prompt = RAG_PROMPT.format(context=context, question=query)
    return chat(prompt, model=model)


def list_indexed_documents() -> list[dict]:
    """Return all documents that have been indexed."""
    db = SessionLocal()
    try:
        docs = db.query(IndexedDocument).order_by(IndexedDocument.indexed_at.desc()).all()
        return [
            {
                "doc_id": d.doc_id,
                "filename": d.filename,
                "chunk_count": d.chunk_count,
                "indexed_at": d.indexed_at.isoformat() if d.indexed_at else None,
            }
            for d in docs
        ]
    finally:
        db.close()

"""
File Manager — Handle uploads, text extraction, and listing.
Supports PDF, DOCX, and plain text files.
"""
import os
import shutil
from io import BytesIO
import fitz          # PyMuPDF
import docx
from app.config import DOCUMENTS_DIR, ENABLE_ENCRYPTION
from app.storage.database import SessionLocal, IndexedDocument


def save_uploaded_file(upload_file) -> str:
    """
    Save an uploaded FastAPI UploadFile to the documents directory.

    Returns:
        Absolute path to the saved file.
    """
    filename = upload_file.filename
    dest_path = os.path.join(DOCUMENTS_DIR, filename)

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    return dest_path


def extract_text(filepath: str) -> str:
    """
    Extract raw text from PDF, DOCX, or TXT file.

    Args:
        filepath: Absolute path to the file.

    Returns:
        Extracted text as a string.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return _extract_docx(filepath)
    elif ext == ".txt":
        return _extract_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: PDF, DOCX, TXT")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """
    Split text into overlapping chunks for LLM processing.

    Args:
        text: Full document text.
        chunk_size: Approximate number of words per chunk.
        overlap: Number of words to overlap between chunks.

    Returns:
        List of text chunks.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap

    return [c for c in chunks if len(c.strip()) > 10]  # ignore tiny chunks


def list_documents() -> list[dict]:
    """Return list of all uploaded files with metadata."""
    files = []
    for fname in os.listdir(DOCUMENTS_DIR):
        fpath = os.path.join(DOCUMENTS_DIR, fname)
        if os.path.isfile(fpath):
            files.append({
                "filename": fname,
                "size_kb": round(os.path.getsize(fpath) / 1024, 2),
                "path": fpath,
            })
    return files


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _extract_pdf(filepath: str) -> str:
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def _extract_docx(filepath: str) -> str:
    doc = docx.Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

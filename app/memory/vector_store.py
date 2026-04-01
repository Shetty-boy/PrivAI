"""
Vector Store — ChromaDB wrapper for document embeddings and semantic search.
"""
import chromadb
from chromadb.config import Settings
from app.config import VECTORSTORE_DIR
from app.models.embedder import embed, embed_single

# ─── ChromaDB Client (persistent, local) ─────────────────────────────────────
_client = None
_collection = None
COLLECTION_NAME = "pai_documents"


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=VECTORSTORE_DIR,
            settings=Settings(anonymized_telemetry=False),  # Privacy: disable telemetry
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(doc_id: str, chunks: list[str]) -> int:
    """
    Embed and store document chunks in ChromaDB.

    Args:
        doc_id: Unique identifier for the document.
        chunks: List of text chunks from the document.

    Returns:
        Number of chunks stored.
    """
    collection = _get_collection()
    embeddings = embed(chunks)

    ids = [f"{doc_id}__chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]

    # Delete existing chunks for this doc (re-indexing support)
    _delete_doc_chunks(doc_id)

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )
    return len(chunks)


def search(query: str, top_k: int = 4) -> list[dict]:
    """
    Semantic search: find the most relevant chunks for a query.

    Returns:
        List of {text, doc_id, score} dicts.
    """
    collection = _get_collection()
    if collection.count() == 0:
        return []

    query_embedding = embed_single(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    output = []
    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "text": doc,
            "doc_id": results["metadatas"][0][i].get("doc_id", "unknown"),
            "score": 1 - results["distances"][0][i],  # cosine similarity
        })
    return output


def get_all_doc_ids() -> list[str]:
    """Return list of unique document IDs stored in the vector store."""
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.get(include=["metadatas"])
    doc_ids = set()
    for meta in results["metadatas"]:
        doc_ids.add(meta.get("doc_id", "unknown"))
    return list(doc_ids)


def _delete_doc_chunks(doc_id: str):
    """Remove all chunks for a given document ID (for re-indexing)."""
    collection = _get_collection()
    try:
        existing = collection.get(where={"doc_id": doc_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

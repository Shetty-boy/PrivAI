"""
Tests for RAG Engine
"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app.memory.vector_store import add_chunks, search


# ─── Vector Store Tests ───────────────────────────────────────────────────────

@patch("app.memory.vector_store.embed")
@patch("app.memory.vector_store._get_collection")
def test_add_chunks_returns_count(mock_get_col, mock_embed):
    mock_embed.return_value = [[0.1, 0.2, 0.3]] * 3
    mock_col = MagicMock()
    mock_col.count.return_value = 0
    mock_get_col.return_value = mock_col

    result = add_chunks("test_doc", ["chunk1", "chunk2", "chunk3"])
    assert result == 3
    mock_col.add.assert_called_once()


@patch("app.memory.vector_store.embed_single")
@patch("app.memory.vector_store._get_collection")
def test_search_returns_empty_on_no_docs(mock_get_col, mock_embed):
    mock_col = MagicMock()
    mock_col.count.return_value = 0
    mock_get_col.return_value = mock_col
    mock_embed.return_value = [0.1, 0.2, 0.3]

    results = search("What is AI?", top_k=4)
    assert results == []


@patch("app.memory.vector_store.embed_single")
@patch("app.memory.vector_store._get_collection")
def test_search_returns_results(mock_get_col, mock_embed):
    mock_col = MagicMock()
    mock_col.count.return_value = 5
    mock_col.query.return_value = {
        "documents": [["Relevant text chunk"]],
        "metadatas": [[{"doc_id": "test_doc", "chunk_index": 0}]],
        "distances": [[0.1]],
    }
    mock_get_col.return_value = mock_col
    mock_embed.return_value = [0.1, 0.2, 0.3]

    results = search("test query", top_k=1)
    assert len(results) == 1
    assert results[0]["text"] == "Relevant text chunk"
    assert results[0]["doc_id"] == "test_doc"
    assert results[0]["score"] == pytest.approx(0.9, abs=0.01)


# ─── Intent Detection Tests ───────────────────────────────────────────────────

from app.agents.intent_detector import _keyword_fallback, _parse_llm_intent

def test_intent_summarize():
    assert _keyword_fallback("please summarize this file") == "summarize"

def test_intent_schedule():
    assert _keyword_fallback("remind me to do homework by friday") == "schedule"

def test_intent_query():
    assert _keyword_fallback("what does the document say about methodology") == "query_document"

def test_intent_list_tasks():
    assert _keyword_fallback("show my tasks list") == "list_tasks"

def test_intent_chat_fallback():
    assert _keyword_fallback("hello there") == "general_chat"

def test_general_question_stays_general_chat():
    assert _keyword_fallback("What is machine learning?") == "general_chat"

def test_task_word_alone_does_not_force_schedule():
    assert _keyword_fallback("What is a task queue?") == "general_chat"

def test_parse_llm_intent_rejects_multi_label_output():
    raw = """
    Response: "Summarize"
    Response: "Schedule"
    Response: "General_Chat"
    """
    assert _parse_llm_intent(raw) is None

def test_parse_llm_intent_accepts_single_label_output():
    assert _parse_llm_intent("general_chat") == "general_chat"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for note summarizer.
"""
import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.file_manager import chunk_text
from app.tools.summarizer import summarize_text


def test_chunk_text_small():
    text = "This is a small text that fits in one chunk."
    chunks = chunk_text(text, chunk_size=100)
    assert len(chunks) == 1
    assert "small text" in chunks[0]


def test_chunk_text_large():
    text = " ".join(["word"] * 2000)
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    assert len(chunks) > 1


def test_chunk_text_filters_tiny():
    text = "  \n  small  \n  "
    chunks = chunk_text(text, chunk_size=100)
    assert len(chunks) == 0


def test_chunk_overlap():
    words = [f"word{i}" for i in range(1000)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) >= 2


@patch("app.tools.summarizer.chat")
def test_summarize_single_chunk(mock_chat):
    mock_chat.side_effect = ["Chunk summary.", "This is the summary."]
    result = summarize_text("Short text to summarize.")
    assert result["summary"] == "This is the summary."
    assert result["chunk_count"] == 1
    assert result["time_seconds"] >= 0


@patch("app.tools.summarizer.chat")
def test_summarize_multi_chunk(mock_chat):
    mock_chat.side_effect = ["Chunk summary."] * 10
    long_text = " ".join(["word"] * 2000)
    result = summarize_text(long_text)
    assert len(result["summary"]) > 0
    assert result["chunk_count"] > 1


@patch("app.tools.summarizer.chat")
def test_summarize_uses_requested_options(mock_chat):
    mock_chat.side_effect = ["Chunk summary.", "Merged summary."]
    result = summarize_text(
        "Short text to summarize.",
        detail_level="detailed",
        format_type="study_guide",
    )
    assert result["detail_level"] == "detailed"
    assert result["format_type"] == "study_guide"
    assert result["summary"] == "Merged summary."


def test_summarize_empty_text():
    result = summarize_text("")
    assert "No content" in result["summary"]
    assert result["chunk_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

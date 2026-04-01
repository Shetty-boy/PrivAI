"""
Summarizer tool with configurable detail and output structure.
"""
import time

from app.config import PRIMARY_MODEL
from app.models.llm_client import chat
from app.storage.file_manager import chunk_text, extract_text

DETAIL_GUIDANCE = {
    "concise": "Keep the output tight and high signal. Prioritize only the most important ideas.",
    "standard": "Balance brevity with clarity. Cover the main ideas with enough detail to understand the document.",
    "detailed": "Be comprehensive. Include major topics, subtopics, supporting details, examples, and notable arguments.",
}

FORMAT_GUIDANCE = {
    "plain": "Write a clean readable summary in prose, with short bullets only when helpful.",
    "structured": """Use this exact structure:
## Overview
## Main Topics
- Topic
  - Subtopics / important details
## Key Takeaways
## Important Details
## Action Items or Open Questions
Prefer clear bullets and include subtopics under each major topic.""",
    "study_guide": """Use this exact structure:
## Big Picture
## Topics and Subtopics
- Topic
  - Definition / explanation
  - Important details
## Terms to Remember
## Possible Questions
## Short Recap
Make it useful for revision and learning.""",
}

CHUNK_SUMMARY_PROMPT = """You are summarizing one chunk from a larger document.
{detail_guidance}

Extract:
- the chunk's main topic
- important subtopics
- key facts, arguments, or decisions
- any dates, action items, or examples

Write a compact chunk summary that will later be merged with other chunk summaries.

Section:
{chunk}

Chunk Summary:"""

MERGE_PROMPT = """You are given multiple chunk summaries from the same document.
Produce one final document summary.

Detail requirement:
{detail_guidance}

Formatting requirement:
{format_guidance}

Chunk Summaries:
{summaries}

Final Summary:"""


def summarize_text(
    text: str,
    model: str = PRIMARY_MODEL,
    detail_level: str = "standard",
    format_type: str = "structured",
) -> dict:
    """
    Summarize raw text with timing info.

    Returns:
        dict with summary metadata.
    """
    start = time.time()
    chunks = chunk_text(text)
    detail_level = detail_level if detail_level in DETAIL_GUIDANCE else "standard"
    format_type = format_type if format_type in FORMAT_GUIDANCE else "structured"

    if not chunks:
        return {
            "summary": "No content found to summarize.",
            "chunk_count": 0,
            "time_seconds": 0,
            "detail_level": detail_level,
            "format_type": format_type,
        }

    chunk_summaries = []
    for chunk in chunks:
        chunk_summary = chat(
            CHUNK_SUMMARY_PROMPT.format(
                chunk=chunk,
                detail_guidance=DETAIL_GUIDANCE[detail_level],
            ),
            model=model,
        )
        chunk_summaries.append(chunk_summary)

    combined = "\n\n---\n\n".join(chunk_summaries)
    summary = chat(
        MERGE_PROMPT.format(
            summaries=combined,
            detail_guidance=DETAIL_GUIDANCE[detail_level],
            format_guidance=FORMAT_GUIDANCE[format_type],
        ),
        model=model,
    )

    elapsed = round(time.time() - start, 2)
    return {
        "summary": summary,
        "chunk_count": len(chunks),
        "time_seconds": elapsed,
        "detail_level": detail_level,
        "format_type": format_type,
    }


def summarize_file(
    filepath: str,
    detail_level: str = "standard",
    format_type: str = "structured",
) -> dict:
    """
    Extract text from a file and return summary metadata.
    """
    text = extract_text(filepath)
    return summarize_text(
        text,
        detail_level=detail_level,
        format_type=format_type,
    )

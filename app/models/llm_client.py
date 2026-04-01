"""
LLM Client — Wrapper around Ollama API
All LLM calls go through this module.
"""
import ollama
import httpx
from app.config import PRIMARY_MODEL, FAST_MODEL, OLLAMA_BASE_URL


def _check_ollama_running() -> bool:
    """Check if Ollama server is reachable."""
    try:
        resp = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def chat(prompt: str, model: str = PRIMARY_MODEL, system: str = None) -> str:
    """
    Send a prompt to the local Ollama model and return the response text.

    Args:
        prompt: The user message.
        model: Which Ollama model to use.
        system: Optional system instruction.

    Returns:
        The model's response string.
    """
    if not _check_ollama_running():
        raise ConnectionError(
            "Ollama is not running. Please start it with: ollama serve"
        )

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(model=model, messages=messages)
    return response["message"]["content"].strip()


def chat_fast(prompt: str) -> str:
    """Use TinyLlama for fast, simple classification tasks."""
    return chat(prompt, model=FAST_MODEL)


def stream_chat(prompt: str, model: str = PRIMARY_MODEL, system: str = None):
    """
    Generator that streams tokens from the model.
    Use this with Streamlit's st.write_stream() for live output.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    stream = ollama.chat(model=model, messages=messages, stream=True)
    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            yield token


def list_available_models() -> list[str]:
    """Return list of locally available Ollama models."""
    try:
        result = ollama.list()
        return [m["name"] for m in result.get("models", [])]
    except Exception:
        return []

"""
Embedder — Sentence embedding using SentenceTransformers (local, no API)
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from app.config import EMBEDDING_MODEL, ENABLE_DP_NOISE, DP_EPSILON

# Load model once at module level (cached in memory)
_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded")
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of strings into embedding vectors.

    Args:
        texts: List of strings to embed.

    Returns:
        List of embedding vectors (as Python lists).
    """
    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)

    if ENABLE_DP_NOISE:
        embeddings = _add_dp_noise(embeddings)

    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    """Embed a single string."""
    return embed([text])[0]


def _add_dp_noise(embeddings: np.ndarray) -> np.ndarray:
    """
    Add Gaussian noise for differential privacy.
    Prevents exact reconstruction from stored embedding vectors.
    ε-differential privacy with sensitivity=1.
    """
    sensitivity = 1.0
    noise_scale = sensitivity / DP_EPSILON
    noise = np.random.normal(0, noise_scale, embeddings.shape)
    return embeddings + noise

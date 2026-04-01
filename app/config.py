"""
App Configuration
"""
import os

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
VECTORSTORE_DIR = os.path.join(DATA_DIR, "vectorstore")
DB_PATH = os.path.join(DATA_DIR, "assistant.db")

# ─── LLM Settings ─────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
PRIMARY_MODEL = "phi3:mini"          # Main reasoning model
FAST_MODEL = "tinyllama"             # Fast intent classification
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ─── RAG Settings ─────────────────────────────────────────────────────────────
CHUNK_SIZE = 800          # tokens per chunk (approx characters/4)
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 4         # How many chunks to retrieve

# ─── Privacy Settings ─────────────────────────────────────────────────────────
ENABLE_ENCRYPTION = False            # Set True to encrypt stored files
ENABLE_DP_NOISE = False             # Set True to add DP noise to embeddings
DP_EPSILON = 1.0                     # Differential privacy parameter

# ─── API Settings ─────────────────────────────────────────────────────────────
API_HOST = "127.0.0.1"
API_PORT = 8000

# ─── Create required directories ──────────────────────────────────────────────
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

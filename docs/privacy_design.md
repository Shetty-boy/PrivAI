# Privacy Design Document

## Privacy Guarantee

The PAI Assistant provides **provably zero data leakage** through architectural,
operational, and cryptographic mechanisms.

## Layer 1: Architectural Privacy (Air-Gap)

All network services are bound to `127.0.0.1` (loopback interface):

| Service | Address | External Access |
|---|---|---|
| Streamlit UI | 127.0.0.1:8501 | ❌ No |
| FastAPI Backend | 127.0.0.1:8000 | ❌ No |
| Ollama LLM | 127.0.0.1:11434 | ❌ No |
| ChromaDB telemetry | Disabled | ❌ No |
| SQLite | Local file | ❌ No |

ChromaDB telemetry is explicitly disabled:
```python
Settings(anonymized_telemetry=False)
```

## Layer 2: Data Isolation

All user data is stored in the `data/` directory:
```
data/
├── documents/     ← Raw uploaded files (on your disk)
├── vectorstore/   ← ChromaDB embeddings (binary, local)
└── assistant.db   ← SQLite: tasks + chat history
```

**To delete all data**: Simply delete the `data/` folder.

## Layer 3: Optional Encryption (AES-256)

Enable by setting `ENABLE_ENCRYPTION = True` in `app/config.py`.

Uses Python `cryptography` library (Fernet = AES-128-CBC + HMAC-SHA256):
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)
encrypted = f.encrypt(plaintext_bytes)
```

Encryption key stored in OS keyring (not in files).

## Layer 4: Optional Differential Privacy (ε-DP)

Enable by setting `ENABLE_DP_NOISE = True` in `app/config.py`.

Gaussian noise is added to embedding vectors before storage in ChromaDB.

**Technical Definition:**
A mechanism M satisfies ε-differential privacy if for all datasets D₁, D₂ differing
by one element, and all outputs S:

```
P[M(D₁) ∈ S] ≤ e^ε × P[M(D₂) ∈ S]
```

With ε=1.0 (default), privacy budget is tight but practical.

**Effect:** Stored embedding vectors cannot be used to reconstruct the original
document text, even if the vector store is compromised.

## Verification

To verify zero outbound connections:
1. Open Wireshark and capture on `lo` (loopback)
2. Run the system and interact with documents
3. Verify: **zero packets** to any external IP address

## What We DO NOT Do

- ❌ No calls to OpenAI, Anthropic, Google, or any cloud API
- ❌ No logging of user data to external servers
- ❌ No analytics or telemetry
- ❌ No cookies or user tracking
- ❌ No API keys required

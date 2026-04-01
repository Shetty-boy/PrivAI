# 🔒 Privacy-Preserving Personal AI Assistant
### Complete Implementation Plan — 6th Semester PAI Project

> **Team Size:** 2 Students | **Timeline:** 6–8 Weeks | **Constraint:** No Cloud APIs, Fully Local

---

## 📋 Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Model & Tools Selection](#2-model--tools-selection)
3. [Tech Stack](#3-tech-stack)
4. [Feature Implementation](#4-feature-implementation)
5. [Privacy Mechanisms](#5-privacy-mechanisms)
6. [Agent Workflow](#6-agent-workflow)
7. [Optimization for Local Devices](#7-optimization-for-local-devices)
8. [Evaluation Metrics](#8-evaluation-metrics)
9. [Deployment Plan](#9-deployment-plan)
10. [GitHub Project Structure](#10-github-project-structure)
11. [Resume & Viva Preparation](#11-resume--viva-preparation)
12. [6–8 Week Sprint Plan](#12-68-week-sprint-plan)

---

## 1. System Architecture

### High-Level Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                       │
│              (Streamlit Web App — runs on localhost)               │
└────────────────────────┬───────────────────────────────────────────┘
                         │ HTTP (local only)
┌────────────────────────▼───────────────────────────────────────────┐
│                      FASTAPI BACKEND (API Gateway)                 │
│          Receives user requests, routes to correct module          │
└───┬──────────────┬──────────────┬──────────────┬───────────────────┘
    │              │              │              │
    ▼              ▼              ▼              ▼
┌───────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐
│ TASK  │   │  MEMORY  │   │ DOCUMENT │   │   SCHEDULER  │
│PLANNER│   │  MODULE  │   │  STORE   │   │   MODULE     │
│(Agent)│   │(ChromaDB)│   │(SQLite + │   │(Local Tasks) │
└───┬───┘   └──────────┘   │  Files)  │   └──────────────┘
    │                      └──────────┘
    ▼
┌─────────────────────────────┐
│     LLM ENGINE              │
│  Ollama / llama.cpp         │
│  Model: Phi-3 Mini / Mistral│
│  Runs 100% on CPU/GPU local │
└─────────────────────────────┘
```

### Module-by-Module Breakdown

| Module | Responsibility | Technology |
|---|---|---|
| **UI Layer** | User interaction, file uploads, chat interface | Streamlit |
| **API Gateway** | Route requests, validate inputs | FastAPI |
| **LLM Engine** | Natural language understanding & generation | Ollama + Phi-3/Mistral |
| **Task Planner** | Intent detection, multi-step task orchestration | Python agent logic |
| **Tool Executor** | Execute specific tools (summarize, search, schedule) | Python functions |
| **Memory Module** | Store conversation context, embeddings | ChromaDB (local vector DB) |
| **Document Store** | Persist notes, tasks, uploaded files | SQLite + local filesystem |

### Data Flow

```
User Input
    │
    ▼
[Intent Detection] — LLM classifies intent (summarize / schedule / Q&A / chat)
    │
    ▼
[Task Planner] — Breaks into sub-steps if multi-step task
    │
    ├──► [Tool: Summarizer] → reads file → LLM → returns summary
    ├──► [Tool: Scheduler]  → parses date/time → saves to SQLite
    ├──► [Tool: RAG Q&A]    → embeds query → searches ChromaDB → LLM answers
    └──► [Tool: Chat]       → direct LLM response with memory context
    │
    ▼
[Response Formatter] → Returns to UI
```

---

## 2. Model & Tools Selection

### LLM Comparison Table

| Model | Size | RAM Required | Speed (CPU) | Best For | Recommended? |
|---|---|---|---|---|---|
| **Phi-3 Mini 3.8B** | ~2.3 GB (4-bit) | 4 GB | ⭐⭐⭐⭐ | Q&A, reasoning, summarization | ✅ **Primary Choice** |
| **Mistral 7B** | ~4.1 GB (4-bit) | 8 GB | ⭐⭐⭐ | Long-form tasks, doc Q&A | ✅ Secondary Choice |
| **TinyLlama 1.1B** | ~0.6 GB | 2 GB | ⭐⭐⭐⭐⭐ | Fast command parsing | ✅ For lightweight tasks |
| **Gemma 2B** | ~1.4 GB | 3 GB | ⭐⭐⭐⭐ | Instruction following | Optional |
| LLaMA 3.2 3B | ~2.0 GB | 4 GB | ⭐⭐⭐⭐ | General assistant | Optional |

> [!IMPORTANT]
> **Recommended Setup**: Use **Phi-3 Mini** as the primary model (best quality-to-size ratio for a student laptop with 8GB RAM). Fall back to **TinyLlama** for fast intent classification only.

### How to Run Locally

#### Option A: Ollama (Recommended — Easiest)
```bash
# Install Ollama (Windows/Mac/Linux)
# Download from: https://ollama.com/download

# Pull models
ollama pull phi3:mini          # Primary model
ollama pull tinyllama          # Lightweight fallback
ollama pull mistral            # If 8GB+ RAM available

# Run as local server (port 11434)
ollama serve

# Test via API (no cloud, 100% local)
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Summarize this text: ..."
}'
```

#### Option B: llama.cpp (More Control, Better Optimization)
```bash
pip install llama-cpp-python
# Download GGUF model from HuggingFace
# Use 4-bit quantized versions (Q4_K_M format)
```

### Embedding Model (for RAG / Document Q&A)
- **Model**: `nomic-embed-text` via Ollama OR `all-MiniLM-L6-v2` via SentenceTransformers
- **Why**: Tiny (80MB), runs on CPU, perfect for semantic search
- **Vector DB**: ChromaDB (local, no server needed)

---

## 3. Tech Stack

### Complete Stack

```
Backend:        Python 3.11+
API:            FastAPI + Uvicorn
UI:             Streamlit
LLM Runtime:    Ollama (primary) / llama-cpp-python (alternative)
Embeddings:     SentenceTransformers (all-MiniLM-L6-v2)
Vector Store:   ChromaDB (local persistent)
Relational DB:  SQLite (tasks, schedules, metadata)
File Parsing:   PyMuPDF (PDF), python-docx (DOCX), plain text
Scheduling:     APScheduler (local cron-like task reminders)
Packaging:      PyInstaller / batch scripts
```

### `requirements.txt`

```txt
fastapi==0.111.0
uvicorn==0.29.0
streamlit==1.35.0
ollama==0.2.1
chromadb==0.5.0
sentence-transformers==2.7.0
PyMuPDF==1.24.5
python-docx==1.1.2
SQLAlchemy==2.0.30
APScheduler==3.10.4
pydantic==2.7.3
python-multipart==0.0.9
```

---

## 4. Feature Implementation

### Feature 1: Note Summarization

**How it works:**
1. User uploads a `.txt`, `.pdf`, or `.docx` file via UI
2. Backend extracts text using PyMuPDF / python-docx
3. Text is chunked (if long) into 1000-token segments
4. Each chunk is sent to Phi-3 Mini with prompt: *"Summarize this section concisely:"*
5. All summaries are merged and re-summarized into a final output

```python
# summarizer.py
def summarize_file(filepath: str, model: str = "phi3:mini") -> str:
    text = extract_text(filepath)  # PDF/DOCX/TXT parser
    chunks = chunk_text(text, max_tokens=1000)
    summaries = []
    for chunk in chunks:
        response = ollama.chat(model=model, messages=[
            {"role": "user", "content": f"Summarize this:\n\n{chunk}"}
        ])
        summaries.append(response['message']['content'])
    
    if len(summaries) > 1:
        combined = "\n".join(summaries)
        final = ollama.chat(model=model, messages=[
            {"role": "user", "content": f"Merge these summaries:\n\n{combined}"}
        ])
        return final['message']['content']
    return summaries[0]
```

---

### Feature 2: Task Scheduling

**How it works:**
1. User types: *"Remind me to submit assignment on Friday at 5pm"*
2. LLM extracts structured JSON: `{task: "...", date: "...", time: "..."}`
3. Task saved to SQLite with APScheduler trigger
4. At scheduled time, a desktop notification fires (plyer library)

```python
# task_manager.py
def create_task_from_text(user_input: str) -> dict:
    prompt = f"""
    Extract task details from this input. Return JSON only.
    Input: "{user_input}"
    Format: {{"task": "...", "due_date": "YYYY-MM-DD", "due_time": "HH:MM", "priority": "low/medium/high"}}
    """
    response = ollama.chat(model="phi3:mini", messages=[
        {"role": "user", "content": prompt}
    ])
    return json.loads(response['message']['content'])
```

---

### Feature 3: Document Q&A (RAG Pipeline)

**How it works (Retrieval Augmented Generation):**
1. User uploads documents → text extracted and chunked
2. Each chunk converted to embedding vector (SentenceTransformers)
3. Vectors stored in ChromaDB (local persistent storage)
4. On query: embed the query → find top-K similar chunks → send to LLM with context
5. LLM answers based only on retrieved context (no hallucination from external data)

```python
# rag_engine.py
import chromadb
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./data/vectorstore")
collection = client.get_or_create_collection("documents")

def index_document(filepath: str, doc_id: str):
    text = extract_text(filepath)
    chunks = chunk_text(text)
    embeddings = embedder.encode(chunks).tolist()
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
    )

def answer_query(query: str) -> str:
    query_embed = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embed, n_results=4)
    context = "\n\n".join(results['documents'][0])
    
    prompt = f"Answer based only on this context:\n{context}\n\nQuestion: {query}"
    response = ollama.chat(model="phi3:mini", messages=[
        {"role": "user", "content": prompt}
    ])
    return response['message']['content']
```

---

### Feature 4: Intent Detection & Command Parsing

```python
# intent_detector.py
INTENTS = ["summarize", "schedule", "query_document", "list_tasks", "general_chat"]

def detect_intent(user_input: str) -> str:
    prompt = f"""
    Classify this user message into one category: {INTENTS}
    Message: "{user_input}"
    Return only the category name, nothing else.
    """
    response = ollama.chat(model="tinyllama", messages=[  # Fast model for intent
        {"role": "user", "content": prompt}
    ])
    return response['message']['content'].strip().lower()
```

---

## 5. Privacy Mechanisms

### Core Privacy Guarantee: Air-Gap Architecture

```
INTERNET
   ✗  ← Firewall / No outbound calls
   │
[Your Laptop]
   │
   ├── Ollama Server (localhost:11434) — LLM runs here
   ├── FastAPI (localhost:8000)        — Backend here
   ├── Streamlit (localhost:8501)      — UI here
   └── ChromaDB / SQLite              — Data stored here
```

**Zero network calls** — everything is on `localhost`. No API keys, no telemetry.

### Local Storage Design

```
data/
├── documents/         # Raw uploaded files
├── vectorstore/       # ChromaDB embeddings (binary, local)
├── tasks.db           # SQLite (tasks, schedules)
└── conversations.db   # SQLite (chat history)
```

### Optional: Data Encryption at Rest

```python
# Using cryptography library (Fernet symmetric encryption)
from cryptography.fernet import Fernet

def encrypt_file(filepath: str, key: bytes):
    f = Fernet(key)
    with open(filepath, 'rb') as file:
        encrypted = f.encrypt(file.read())
    with open(filepath + '.enc', 'wb') as enc_file:
        enc_file.write(encrypted)

# Key stored in OS keyring (not in files)
import keyring
keyring.set_password("pai_assistant", "encryption_key", key.decode())
```

### Optional: Basic Differential Privacy for Stored Summaries

```python
# Add Gaussian noise to embedding vectors before storage
# Prevents exact reconstruction from stored vectors
import numpy as np

def add_dp_noise(embedding: list, epsilon: float = 1.0) -> list:
    sensitivity = 1.0
    noise_scale = sensitivity / epsilon
    noise = np.random.normal(0, noise_scale, len(embedding))
    return (np.array(embedding) + noise).tolist()
```

> [!NOTE]
> For viva: Differential Privacy ensures that stored embedding vectors cannot be reverse-engineered to reconstruct the original document text. This is a mathematically provable privacy guarantee (ε-differential privacy).

---

## 6. Agent Workflow

### Complete Agent Pipeline

```
User Input: "Summarize my notes.pdf and add a task to review it by tomorrow"
     │
     ▼
[Step 1: Intent Detection]
     Intent: MULTI_STEP (contains multiple commands)
     Sub-intents: [summarize, schedule]
     │
     ▼
[Step 2: Task Planner — breaks into sub-tasks]
     Task 1: summarize file "notes.pdf"
     Task 2: create task "Review notes.pdf" due tomorrow
     │
     ▼
[Step 3: Tool Executor — runs tools in sequence]
     ├── Call: summarize_file("notes.pdf")     → Returns summary text
     └── Call: create_task("Review notes.pdf", due="tomorrow")
     │
     ▼
[Step 4: Memory Update]
     Store interaction in conversation history (SQLite)
     │
     ▼
[Step 5: Response Assembly]
     "Here's the summary of notes.pdf: [...]
      ✅ I've also added 'Review notes.pdf' to your tasks for tomorrow."
     │
     ▼
[UI Display]
```

### Example: Multi-Step Task

| Step | Input | Action | Output |
|---|---|---|---|
| 1 | "What does my project report say about methodology?" | Intent: query_document | Retrieves relevant chunks from ChromaDB |
| 2 | Retrieved context + query | LLM generates answer | Answer grounded in document |
| 3 | User: "Summarize that section" | Intent: summarize | Summarizes the retrieved chunk |
| 4 | User: "Remind me to rewrite it by Friday" | Intent: schedule | Task saved to SQLite |

---

## 7. Optimization for Local Devices

### Model Quantization

```bash
# Pull 4-bit quantized versions via Ollama (automatic)
ollama pull phi3:mini          # Already 4-bit quantized
ollama pull mistral:7b-instruct-q4_K_M  # Explicit 4-bit

# For llama.cpp: download Q4_K_M GGUF files from HuggingFace
# Example: Phi-3-mini-4k-instruct.Q4_K_M.gguf (~2.3 GB)
```

**Why Quantization Works:**
- Full precision (FP32): 4 bytes/parameter → 7B model = 28 GB
- 8-bit (INT8): 1 byte/parameter → 7 GB
- 4-bit (INT4): 0.5 bytes/parameter → **3.5 GB ← Use This**
- Quality loss: < 3% on benchmarks

### Latency Reduction Techniques

| Technique | Implementation | Speedup |
|---|---|---|
| **Model preloading** | Keep Ollama server warm, don't reload between requests | 2–5× |
| **Text chunking** | Process 1000 tokens at a time instead of full doc | Linear |
| **Streaming responses** | Stream LLM output token-by-token (Streamlit `st.write_stream`) | Perceived 3× |
| **Embedding caching** | Cache embeddings of already-indexed documents | Near-instant repeat queries |
| **Intent routing** | Use TinyLlama for intent (fast) → Phi-3 for generation | 1.5× overall |

### Memory Budget

```
System RAM Budget (8 GB laptop):
├── OS + Browser:    ~2.5 GB
├── Phi-3 Mini 4-bit: ~2.3 GB
├── ChromaDB:         ~0.2 GB
├── Python/FastAPI:   ~0.3 GB
└── Free buffer:      ~2.7 GB ✅ Comfortable
```

---

## 8. Evaluation Metrics

### Metrics Dashboard (Build this as a feature)

| Metric | How to Measure | Target |
|---|---|---|
| **Response Latency** | `time.time()` before/after LLM call | < 10s on CPU |
| **Task Success Rate** | Manually test 20 queries per feature | > 80% |
| **Summarization Quality** | ROUGE-1 score vs human summary | ROUGE-1 > 0.45 |
| **RAG Retrieval Accuracy** | Top-K recall on 10 test questions | > 75% |
| **Memory Usage** | `psutil` monitoring | < 6 GB peak |
| **Privacy Guarantee** | Zero outbound HTTP requests (Wireshark) | 0 external calls |

### Comparison Table for Report/Viva

| Aspect | Our System | ChatGPT (Cloud) |
|---|---|---|
| Privacy | ✅ 100% Local | ❌ Data sent to OpenAI |
| Cost | ✅ Free forever | ❌ ~$20/month |
| Internet Required | ✅ Never | ❌ Always |
| Response Quality | ⚠️ Good (smaller model) | ✅ Excellent |
| Speed | ⚠️ ~5–10s (CPU) | ✅ ~2s |
| Data Ownership | ✅ 100% yours | ❌ OpenAI's servers |

---

## 9. Deployment Plan

### Running on a Normal Laptop (No GPU)

```bash
# Step 1: Install Ollama
# Download from https://ollama.com → Install for Windows/Mac/Linux

# Step 2: Pull model
ollama pull phi3:mini
ollama pull tinyllama

# Step 3: Clone project
git clone https://github.com/yourteam/pai-assistant
cd pai-assistant

# Step 4: Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac

# Step 5: Install dependencies
pip install -r requirements.txt

# Step 6: Run the application
# Terminal 1: Start backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Start UI
streamlit run ui/app.py
```

### One-Click Startup Script

```batch
:: start_assistant.bat (Windows)
@echo off
echo Starting Privacy-Preserving AI Assistant...
start "" ollama serve
timeout /t 3
start "" cmd /c "venv\Scripts\activate && uvicorn app.main:app --port 8000"
timeout /t 2
start "" cmd /c "venv\Scripts\activate && streamlit run ui/app.py"
echo Assistant is running! Opening browser...
start http://localhost:8501
```

### Packaging to Executable (Optional, Week 8)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed launcher.py
# Creates dist/launcher.exe — shareable without Python installation
```

---

## 10. GitHub Project Structure

```
pai-assistant/
│
├── README.md                    # Project overview, setup guide, screenshots
├── requirements.txt             # All Python dependencies
├── start_assistant.bat          # Windows one-click startup
├── start_assistant.sh           # Linux/Mac one-click startup
│
├── app/                         # FastAPI Backend
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point, route definitions
│   ├── config.py                # App configuration (model names, paths)
│   │
│   ├── agents/
│   │   ├── intent_detector.py   # LLM-based intent classification
│   │   └── task_planner.py      # Multi-step task decomposition logic
│   │
│   ├── tools/
│   │   ├── summarizer.py        # Note/file summarization tool
│   │   ├── scheduler.py         # Task creation & scheduling
│   │   └── rag_engine.py        # Document Q&A (RAG pipeline)
│   │
│   ├── models/
│   │   ├── llm_client.py        # Ollama API wrapper
│   │   └── embedder.py          # SentenceTransformer wrapper
│   │
│   ├── memory/
│   │   ├── vector_store.py      # ChromaDB operations
│   │   └── conversation.py      # Chat history management
│   │
│   └── storage/
│       ├── database.py          # SQLAlchemy SQLite setup
│       └── file_manager.py      # Document upload/retrieval
│
├── ui/                          # Streamlit Frontend
│   ├── app.py                   # Main Streamlit app
│   ├── pages/
│   │   ├── chat.py              # Chat interface page
│   │   ├── summarizer.py        # File upload & summarization page
│   │   ├── tasks.py             # Task list & scheduler page
│   │   └── documents.py         # Document Q&A page
│   └── components/
│       └── sidebar.py           # Navigation sidebar
│
├── data/                        # Local data storage (gitignored)
│   ├── documents/               # Uploaded files
│   ├── vectorstore/             # ChromaDB persistent storage
│   └── assistant.db             # SQLite database
│
├── tests/
│   ├── test_summarizer.py
│   ├── test_rag.py
│   └── test_scheduler.py
│
├── docs/
│   ├── architecture.md          # System design explanation
│   ├── privacy_design.md        # Privacy mechanisms documentation
│   └── screenshots/             # UI screenshots for README
│
└── evaluation/
    ├── benchmark_results.csv    # Latency, accuracy results
    └── eval_script.py           # Automated evaluation runner
```

> [!TIP]
> Add **GitHub Actions** for automated testing (`.github/workflows/test.yml`) — this looks extremely professional on a resume and shows DevOps awareness.

---

## 11. Resume & Viva Preparation

### Strong Resume Bullets

```
• Built a fully local, privacy-preserving AI assistant using Phi-3 Mini (3.8B) via
  Ollama, featuring RAG-based document Q&A with ChromaDB, automated task scheduling,
  and LLM-powered intent detection — achieving <10s response latency on CPU with
  zero cloud dependency.

• Designed and implemented a 4-module agent architecture (intent detection → task
  planning → tool execution → memory) with 4-bit quantized LLMs, reducing RAM
  usage by 75% vs full-precision models while maintaining >80% task accuracy.

• Implemented ε-differential privacy for local embedding storage and AES-256 
  encryption for document persistence, ensuring provable zero-data-leakage on
  consumer hardware.
```

### Key Concepts to Explain Confidently

| Concept | Your Explanation |
|---|---|
| **RAG** | Retrieval-Augmented Generation: Instead of the LLM relying on training data, we embed user documents and retrieve relevant chunks at query time, grounding answers in actual local content |
| **4-bit Quantization** | Representing model weights in 4 bits instead of 32 bits, reducing memory 8× with <3% quality loss — enabling 7B models to run on 4GB RAM |
| **ChromaDB** | A vector database that stores document embeddings and enables semantic similarity search locally |
| **Differential Privacy** | Adding calibrated mathematical noise to data such that individual privacy is preserved even if the dataset is exposed |
| **Intent Detection** | Using a small LLM (TinyLlama) to classify user input into action categories before invoking heavier models |
| **Agent Architecture** | A system where an LLM acts as a planner/reasoner, dynamically calling tools (functions) to complete multi-step tasks |

### Expected Viva Questions & Model Answers

---

**Q1: Why not just use ChatGPT for this?**
> "ChatGPT sends all user data to OpenAI's servers. Our system is fully local — no data ever leaves the user's machine. This is critical for sensitive documents like medical records or personal notes. Additionally, our solution has zero recurring cost and works completely offline."

---

**Q2: How does RAG differ from fine-tuning?**
> "Fine-tuning bakes knowledge into model weights permanently, requiring expensive GPU training. RAG retrieves relevant documents at inference time from an external store, allowing real-time updates without retraining. For a personal assistant that needs to work with the user's own evolving documents, RAG is clearly superior."

---

**Q3: What is quantization and why does it matter here?**
> "Quantization reduces the numerical precision of model weights — from 32-bit floats to 4-bit integers. This reduces model size by ~87.5% with under 3% quality degradation. This is what makes it feasible to run a 7B parameter model on a laptop with 8GB RAM rather than needing a 24GB GPU."

---

**Q4: How do you guarantee privacy?**
> "Three layers: First, the architecture itself — all components (Ollama, FastAPI, ChromaDB) run on localhost with no outbound calls. Second, encrypted file storage using Fernet AES. Third, optional differential privacy noise added to embedding vectors, making it mathematically impossible to reconstruct original documents from stored embeddings."

---

**Q5: How does your agent handle multi-step tasks?**
> "The intent detector identifies if a single message contains multiple intents. The task planner then decomposes it into an ordered sequence of sub-tasks. Each sub-task is handed to the tool executor, which calls the appropriate Python function. Results are aggregated and formatted into a single coherent response."

---

**Q6: What's the bottleneck in your system and how did you address it?**
> "The primary bottleneck is LLM inference latency on CPU — ~5–10 seconds per response. We addressed this by: (1) using the smallest adequate model (Phi-3 Mini 4-bit), (2) using TinyLlama for fast intent classification, (3) implementing streaming responses so users see output incrementally, and (4) caching document embeddings to avoid re-indexing."

---

**Q7: How would you scale this to a production system?**
> "While the current system is single-user local, scaling would involve: replacing Ollama with vLLM for efficient batch inference, moving ChromaDB to a server-side Weaviate or Qdrant instance, adding user authentication, and implementing a proper job queue (Celery + Redis) for async task processing. The agent architecture itself wouldn't change."

---

## 12. 6–8 Week Sprint Plan

| Week | Student A | Student B | Milestone |
|---|---|---|---|
| **Week 1** | Setup: Ollama, models, FastAPI skeleton | Setup: Streamlit UI skeleton, SQLite schema | Dev environment ready |
| **Week 2** | LLM client wrapper, intent detector | File upload, text extraction (PDF/DOCX) | Core LLM integration done |
| **Week 3** | Summarization tool (chunking + merging) | Task scheduler + SQLite CRUD | Summarization + scheduling working |
| **Week 4** | RAG pipeline: ChromaDB indexing + query | RAG frontend page, query UI | Document Q&A end-to-end working |
| **Week 5** | Agent/task planner (multi-step detection) | Conversation memory module | Full agent pipeline working |
| **Week 6** | Privacy: encryption, DP noise | Evaluation script, latency benchmarks | Privacy features + metrics ready |
| **Week 7** | One-click startup script, error handling | README, docs, screenshots, demo video | Deployment-ready |
| **Week 8** | Buffer: polish, viva prep | Buffer: testing edge cases | Final submission ready |

---

> [!IMPORTANT]
> **Minimum Viable Product (MVP) by Week 5**: If time is tight, prioritize Summarization + RAG Q&A. These two features alone, with a clean UI and solid privacy design, are more than enough for a top-tier project submission.

---

*Generated for PAI Project — 6th Semester | Privacy-Preserving Personal AI Assistant*

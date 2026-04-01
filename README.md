# Privacy-Preserving Personal AI Assistant

> A fully local, privacy-first AI assistant that runs entirely on your laptop — no cloud APIs, no data leakage.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Local Chat** | Conversational AI powered by Phi-3 Mini — fully offline |
| 📝 **Note Summarization** | Upload PDF/DOCX/TXT files and get instant summaries |
| 📅 **Task Scheduler** | Natural language task creation with due dates |
| 🔍 **Document Q&A** | Ask questions about your uploaded documents (RAG) |
| 🔒 **Zero Data Leakage** | Everything stays on your machine — always |

---

## 🏗 Architecture

```
Streamlit UI (localhost:8501)
       ↓
FastAPI Backend (localhost:8000)
       ↓
Intent Detector → Task Planner → Tool Executor
                                      ↓
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
              Summarizer           RAG Engine        Scheduler
                    ↓                 ↓                 ↓
              Ollama LLM         ChromaDB          SQLite DB
              (Phi-3 Mini)      (Embeddings)       (Tasks)
              [FULLY LOCAL]     [FULLY LOCAL]    [FULLY LOCAL]
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/download) installed and running

### 1. Pull Required Models
```bash
ollama pull phi3:mini
ollama pull tinyllama
```

### 2. Setup Project
```bash
git clone https://github.com/yourteam/pai-assistant
cd pai-assistant
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Run (Windows — One Click)
```bash
start_assistant.bat
```

### 3. Run (Manual)
```bash
# Terminal 1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2
streamlit run ui/app.py
```

Open **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
pai-assistant/
├── app/                    # FastAPI Backend
│   ├── agents/             # Intent detection + task planning
│   ├── tools/              # Summarizer, RAG, Scheduler
│   ├── models/             # LLM + Embedder clients
│   ├── memory/             # Vector store + conversation history
│   └── storage/            # SQLite + file management
├── ui/                     # Streamlit Frontend
│   ├── pages/              # Feature pages
│   └── components/         # Shared UI components
├── data/                   # Local storage (gitignored)
├── tests/                  # Unit tests
├── docs/                   # Architecture & privacy docs
└── evaluation/             # Benchmarking scripts
```

---

## 🔒 Privacy Guarantees

1. **Air-gap Architecture**: All services run on `localhost` — zero outbound HTTP requests
2. **No API Keys**: No cloud tokens, no accounts required
3. **Local Storage**: All data stored in `data/` on your machine
4. **Optional Encryption**: AES-256 file encryption (set `ENABLE_ENCRYPTION=True` in config)
5. **Optional DP Noise**: Differential privacy on embedding vectors

---

## 🧠 Models Used

| Model | Use | Size |
|---|---|---|
| Phi-3 Mini (4-bit) | Main reasoning, summarization, Q&A | ~2.3 GB |
| TinyLlama (4-bit) | Fast intent classification | ~0.6 GB |
| all-MiniLM-L6-v2 | Sentence embeddings for RAG | ~80 MB |

---

## 📊 Performance

| Metric | Value |
|---|---|
| Response Latency (CPU) | 5–12 seconds |
| RAM Usage (peak) | ~4.5 GB |
| Document Q&A Accuracy | >75% Top-K recall |
| Task Parsing Accuracy | >85% |

---

## 👥 Team

- **Student A** — Backend, LLM Integration, Agent Architecture
- **Student B** — Frontend, Storage, Evaluation

---

*Built for PAI Project — 6th Semester*

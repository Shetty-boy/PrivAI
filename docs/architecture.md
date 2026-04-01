# System Architecture

## Overview

The PAI Assistant follows a modular layered architecture where all components communicate
exclusively over `localhost`. No outbound internet connections are made at any point.

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER              │
│   Streamlit UI — localhost:8501         │
│   4 pages: Chat, Summarize, Tasks, RAG  │
└─────────────┬───────────────────────────┘
              │ HTTP (loopback only)
┌─────────────▼───────────────────────────┐
│         APPLICATION LAYER               │
│   FastAPI — localhost:8000              │
│   REST API: /chat /summarize /tasks     │
│             /documents /history        │
└──┬─────┬──────┬──────┬──────────────────┘
   │     │      │      │
   ▼     ▼      ▼      ▼
┌─────┐ ┌────┐ ┌────┐ ┌────────┐
│Agent│ │RAG │ │Task│ │Memory  │
│Layer│ │Eng.│ │Mgr │ │Layer   │
└──┬──┘ └─┬──┘ └─┬──┘ └───┬────┘
   │      │      │        │
   ▼      ▼      │        ▼
┌─────────────────┐│  ┌──────────┐
│  LLM Engine     ││  │ SQLite   │
│  Ollama         ││  │ Database │
│  localhost:11434││  └──────────┘
└─────────────────┘│
                   ▼
              ┌──────────┐
              │ ChromaDB │
              │ VectorDB │
              │ (local)  │
              └──────────┘
```

## Module Descriptions

### 1. UI Layer (Streamlit)
- **Chat**: Conversational interface with session memory and intent display
- **Summarizer**: File upload → LLM summarization
- **Tasks**: NLP-powered task creation and management
- **Documents Q&A**: RAG pipeline with indexed documents

### 2. API Gateway (FastAPI)
- Receives all UI requests
- Validates inputs with Pydantic models
- Routes to correct business logic module
- Returns structured JSON responses

### 3. Agent Layer
- **Intent Detector**: Uses TinyLlama to classify user queries into 6 intent categories
- **Task Planner**: Decomposes intents into tool calls; handles multi-step tasks

### 4. Tool Layer
- **Summarizer**: Chunk → per-chunk LLM summary → merge summary
- **RAG Engine**: Embed → retrieve → generate grounded answer
- **Scheduler**: NLP parsing → JSON extraction → SQLite persistence

### 5. Model Layer
- **LLM Client**: Ollama wrapper for Phi-3 Mini and TinyLlama
- **Embedder**: SentenceTransformers (all-MiniLM-L6-v2) for vector embeddings

### 6. Memory Layer
- **Vector Store**: ChromaDB for persistent semantic document search
- **Conversation**: SQLite-backed chat history with session support

### 7. Storage Layer
- **Database**: SQLAlchemy + SQLite for tasks and conversation history
- **File Manager**: Text extraction (PDF/DOCX/TXT) and intelligent chunking

## Data Flow Example: Document Q&A

```
User: "What does my report say about results?"
  │
  ├─[1] Intent Detection (TinyLlama, ~2s)
  │       → "query_document"
  │
  ├─[2] Task Planner routes to RAG Engine
  │
  ├─[3] Embed query (all-MiniLM-L6-v2, ~0.1s)
  │       → [0.23, -0.11, 0.89, ...]
  │
  ├─[4] ChromaDB cosine similarity search (~0.05s)
  │       → Top 4 matching chunks from indexed documents
  │
  ├─[5] Phi-3 Mini generates answer (~8s on CPU)
  │       Context: [retrieved chunks]
  │       Prompt: "Answer only from context: ..."
  │
  └─[6] Return grounded answer to UI
```

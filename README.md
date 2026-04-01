# PrivAI

Privacy-first personal AI assistant that runs fully on your machine with local models, local storage, and a modular multi-agent backend.

## What It Does

- Local chat with a general conversation agent
- Document summarization with configurable depth and output format
- Task creation from natural language with editable due date, time, priority, and status
- Document question answering with local RAG
- Agent handoff tracing in chat so you can see which specialist agent handled a request

## Architecture

The app uses a small coordinator plus specialist agents:

- `intent_detector`: classifies the user request
- `task_planner`: coordinator/orchestrator
- `general_chat_agent`: handles open-ended chat
- `scheduler_agent`: creates tasks from natural language
- `task_manager_agent`: lists and deletes tasks
- `document_qa_agent`: answers questions from indexed documents
- `summarizer_agent`: routes users into the summarizer workflow

Core stack:

- `FastAPI` backend
- `Streamlit` frontend
- `Ollama` for local LLM inference
- `ChromaDB` for document retrieval
- `SQLite` for tasks and conversation history
- `SentenceTransformers` for embeddings

## Key Features

### 1. Multi-Agent Chat Routing

Requests are first classified by intent and then routed to a specialist agent. The chat UI shows:

- detected intent
- handling agent
- agent handoff trace

### 2. Configurable Summarization

The summarizer now supports:

- detail levels: `concise`, `standard`, `detailed`
- formats: `plain`, `structured`, `study_guide`

This makes it possible to get topic-wise and subtopic-wise summaries instead of one flat output.

### 3. Better Task Handling

Tasks support:

- natural language creation
- deterministic weekday parsing for prompts like `on monday`
- direct editing from the UI
- priority and status updates

## Project Structure

```text
PrivAI-main/
├── app/
│   ├── agents/
│   ├── memory/
│   ├── models/
│   ├── storage/
│   ├── tools/
│   └── main.py
├── ui/
│   ├── components/
│   ├── pages/
│   └── app.py
├── docs/
├── evaluation/
├── tests/
├── requirements.txt
└── README.md
```

## Run Locally

### Prerequisites

- Python 3.11+
- Ollama installed and running

### Pull Local Models

```powershell
ollama pull phi3:mini
ollama pull tinyllama
```

### Install Dependencies

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Start Backend

```powershell
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Start Frontend

```powershell
venv\Scripts\python.exe -m streamlit run ui/app.py --server.port 8501
```

Open:

- UI: `http://127.0.0.1:8501`
- API docs: `http://127.0.0.1:8000/docs`

## Privacy Notes

- No cloud API keys required
- Data stays on your device
- Documents are processed locally
- Tasks and history are stored locally

## Current State

This repo currently includes:

- modular specialist agents
- task editing support
- improved summarization controls
- chat handoff tracing

## License

MIT

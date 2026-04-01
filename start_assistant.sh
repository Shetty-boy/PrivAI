#!/bin/bash
echo "============================================"
echo "  PAI Assistant - Privacy-Preserving AI"
echo "============================================"

# Start Ollama
echo "[1/3] Starting Ollama..."
ollama serve &
sleep 3

# Start FastAPI
echo "[2/3] Starting FastAPI backend..."
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 3

# Start Streamlit
echo "[3/3] Starting Streamlit UI..."
streamlit run ui/app.py --server.port 8501 &
sleep 2

echo "All services running!"
echo "  UI:  http://localhost:8501"
echo "  API: http://localhost:8000"

# Open browser
xdg-open http://localhost:8501 2>/dev/null || open http://localhost:8501 2>/dev/null
wait

@echo off
title PAI Assistant - Privacy-Preserving AI
color 0A
echo.
echo ============================================
echo   PAI Assistant - Starting Up
echo   Privacy-Preserving AI - Fully Local
echo ============================================
echo.

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b
)

:: Start Ollama in background
echo [1/3] Starting Ollama LLM server...
start "" /min cmd /c "ollama serve"
timeout /t 3 /nobreak > nul

:: Start FastAPI backend
echo [2/3] Starting FastAPI backend (port 8000)...
start "" /min cmd /k "venv\Scripts\activate && uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 4 /nobreak > nul

:: Start Streamlit UI
echo [3/3] Starting Streamlit UI (port 8501)...
start "" cmd /k "venv\Scripts\activate && streamlit run ui/app.py --server.port 8501"
timeout /t 3 /nobreak > nul

:: Open browser
echo.
echo ============================================
echo   All services started!
echo   Opening browser...
echo ============================================
start http://localhost:8501

echo.
echo Services running at:
echo   UI:      http://localhost:8501
echo   API:     http://localhost:8000
echo   Docs:    http://localhost:8000/docs
echo   Ollama:  http://localhost:11434
echo.
echo Press any key to open the API docs...
pause > nul
start http://localhost:8000/docs

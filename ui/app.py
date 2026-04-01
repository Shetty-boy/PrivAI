"""
Main Streamlit Application — Entry Point
Provides a premium dark-themed UI with navigation.
"""
import streamlit as st
import sys
import os

# ─── Page Config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="PAI Assistant — Private AI on Your Device",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Add project root to path ─────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b27 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Cards */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.3s;
}
.card:hover { border-color: rgba(99,102,241,0.5); }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.1));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #818cf8; }
.metric-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; }

/* Privacy badge */
.privacy-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.15);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    color: #4ade80;
    font-weight: 500;
}

/* Headings */
h1, h2, h3 { color: #e2e8f0 !important; }
h1 { font-weight: 700 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s !important;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important; }

/* Chat messages */
.stChatMessage { background: rgba(255,255,255,0.04) !important; border-radius: 12px !important; }

/* Text inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(99,102,241,0.08) !important;
    border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
}

/* Alert/info boxes */
.stAlert { border-radius: 10px !important; }

/* Success messages */
.element-container .stSuccess { background: rgba(34,197,94,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─── Import Pages ─────────────────────────────────────────────────────────────
from ui.pages.chat import render_chat_page
from ui.pages.summarizer import render_summarizer_page
from ui.pages.tasks import render_tasks_page
from ui.pages.documents import render_documents_page
from ui.components.sidebar import render_sidebar

# ─── Sidebar Navigation ───────────────────────────────────────────────────────
page = render_sidebar()

# ─── Route to Pages ───────────────────────────────────────────────────────────
if page == "Chat":
    render_chat_page()
elif page == "Summarizer":
    render_summarizer_page()
elif page == "Tasks":
    render_tasks_page()
elif page == "Documents Q&A":
    render_documents_page()

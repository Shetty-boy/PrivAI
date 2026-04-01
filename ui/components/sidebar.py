"""
Sidebar Component — Navigation + Status Panel
"""
import streamlit as st
import httpx
from app.config import API_HOST, API_PORT
from app.models.llm_client import list_available_models


def render_sidebar() -> str:
    """Render the navigation sidebar and return the selected page name."""

    with st.sidebar:
        # ── Logo / Header ────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
            <div style="font-size: 3rem;">🔒</div>
            <h2 style="margin:0; font-size:1.3rem; font-weight:700; color:#818cf8;">PAI Assistant</h2>
            <p style="margin:0; font-size:0.7rem; color:#64748b; letter-spacing:0.1em;">PRIVACY-PRESERVING AI</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Privacy Status Badge ─────────────────────────────────────────────
        st.markdown("""
        <div class="privacy-badge" style="margin-bottom:1.5rem; width:100%; justify-content:center;">
            🟢 100% Local · Zero Cloud
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ───────────────────────────────────────────────────────
        st.markdown("### 🧭 Navigation")
        pages = {
            "💬 Chat": "Chat",
            "📝 Summarizer": "Summarizer",
            "📅 Tasks": "Tasks",
            "🔍 Documents Q&A": "Documents Q&A",
        }

        if "selected_page" not in st.session_state:
            st.session_state.selected_page = "Chat"

        for label, value in pages.items():
            is_active = st.session_state.selected_page == value
            btn_style = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{value}", use_container_width=True, type=btn_style):
                st.session_state.selected_page = value
                st.rerun()

        st.divider()

        # ── System Status ────────────────────────────────────────────────────
        st.markdown("### ⚙️ System Status")

        # Check backend
        backend_ok = _check_backend()
        backend_icon = "🟢" if backend_ok else "🔴"
        st.markdown(f"{backend_icon} **Backend API** — {'Online' if backend_ok else 'Offline'}")

        # Check Ollama + models
        models = list_available_models()
        if models:
            st.markdown(f"🟢 **Ollama** — {len(models)} model(s)")
            for m in models[:3]:
                st.markdown(f"  &nbsp;&nbsp;• `{m}`", unsafe_allow_html=True)
        else:
            st.markdown("🔴 **Ollama** — Not running")
            st.caption("Run: `ollama serve`")

        st.divider()

        # ── Info ─────────────────────────────────────────────────────────────
        st.markdown("### ℹ️ About")
        st.caption(
            "All data stays on your device. "
            "No internet required. "
            "No API keys needed."
        )
        st.caption("PAI Project · 6th Semester")

    return st.session_state.selected_page


def _check_backend() -> bool:
    try:
        resp = httpx.get(f"http://{API_HOST}:{API_PORT}/health", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False

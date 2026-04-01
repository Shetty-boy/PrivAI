"""
Chat page with intent labels and agent handoff tracing.
"""
import httpx
import streamlit as st

from app.config import API_HOST, API_PORT

API_BASE = f"http://{API_HOST}:{API_PORT}"
SESSION_ID = "main_session"

INTENT_LABELS = {
    "summarize": ("Summarize", "#f59e0b"),
    "schedule": ("Schedule", "#10b981"),
    "query_document": ("Doc Search", "#6366f1"),
    "list_tasks": ("List Tasks", "#8b5cf6"),
    "delete_task": ("Delete Task", "#ef4444"),
    "general_chat": ("Chat", "#64748b"),
}


def render_chat_page():
    st.markdown(
        """
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">Chat with Your AI</h1>
    <p style="color:#94a3b8; margin-bottom:1.5rem;">
        Ask anything, create tasks, search documents - all privately on your device.
    </p>
    """,
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state or not st.session_state.messages:
        st.markdown("**Try asking:**")
        cols = st.columns(3)
        examples = [
            "What is machine learning?",
            "Remind me to submit report by Friday",
            "What does my project file say about methodology?",
        ]
        for idx, example in enumerate(examples):
            if cols[idx].button(f'"{example}"', key=f"ex_{idx}", use_container_width=True):
                _send_message(example)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("intent"):
                _render_intent_badge(msg["intent"])
            if msg["role"] == "assistant":
                _render_agent_trace(msg.get("agent_display_name"), msg.get("handoff_trace"))

    if prompt := st.chat_input("Ask me anything..."):
        _send_message(prompt)

    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Clear", key="clear_chat"):
            st.session_state.messages = []
            try:
                httpx.delete(f"{API_BASE}/history/{SESSION_ID}", timeout=5)
            except Exception:
                pass
            st.rerun()


def _render_intent_badge(intent: str):
    label, color = INTENT_LABELS.get(intent, ("Chat", "#64748b"))
    st.markdown(
        f'<span style="font-size:0.7rem; color:{color}; border:1px solid {color}40; '
        f'border-radius:8px; padding:2px 8px;">Detected: {label}</span>',
        unsafe_allow_html=True,
    )


def _render_agent_trace(agent_display_name: str | None, handoff_trace: list | None):
    if agent_display_name:
        st.caption(f"Handled By: {agent_display_name}")
    if handoff_trace:
        lines = []
        for step in handoff_trace:
            stage = step.get("stage", "step").replace("_", " ").title()
            agent = step.get("agent", "agent")
            detail = step.get("detail", "")
            lines.append(f"- **{stage}** via `{agent}`: {detail}")
        with st.expander("Agent Trace", expanded=False):
            st.markdown("\n".join(lines))


def _send_message(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking locally..."):
            try:
                resp = httpx.post(
                    f"{API_BASE}/chat",
                    json={"message": prompt, "session_id": SESSION_ID},
                    timeout=120,
                )
                data = resp.json()
                reply = data.get("reply", "Sorry, I couldn't generate a response.")
                intent = data.get("intent", "general_chat")
                agent_display_name = data.get("agent_display_name")
                handoff_trace = data.get("handoff_trace", [])
            except httpx.ConnectError:
                reply = "Backend is not running. Start it with: `uvicorn app.main:app --port 8000`"
                intent = "general_chat"
                agent_display_name = "Unavailable"
                handoff_trace = []
            except Exception as exc:
                reply = f"Error: {str(exc)}"
                intent = "general_chat"
                agent_display_name = "Unavailable"
                handoff_trace = []

        st.markdown(reply)
        _render_intent_badge(intent)
        _render_agent_trace(agent_display_name, handoff_trace)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
            "intent": intent,
            "agent_display_name": agent_display_name,
            "handoff_trace": handoff_trace,
        }
    )

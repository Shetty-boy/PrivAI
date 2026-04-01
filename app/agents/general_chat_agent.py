"""
General conversation agent.
"""
from app.agents.agent_result import AgentExecutionResult, AgentTraceStep
from app.memory.conversation import get_history
from app.models.llm_client import chat

CHAT_SYSTEM_PROMPT = """You are a helpful, friendly, and concise personal AI assistant running entirely on the user's local machine.
You have access to the user's notes, tasks, and documents, all stored privately on their device.
No data ever leaves their machine. Be helpful, accurate, and to the point.
Today's context is provided in the conversation history."""


def handle_general_chat(message: str, session_id: str = "default") -> AgentExecutionResult:
    history = get_history(session_id, limit=6)
    context_lines = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        context_lines.append(f"{role}: {msg['content']}")
    context = "\n".join(context_lines)
    prompt = f"{context}\nUser: {message}" if context else message
    reply = chat(prompt, system=CHAT_SYSTEM_PROMPT)
    return AgentExecutionResult(
        reply=reply,
        agent_name="general_chat_agent",
        agent_display_name="General Chat Agent",
        handoff_trace=[
            AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to general conversation"),
            AgentTraceStep(stage="execution", agent="general_chat_agent", detail="Answered with conversation memory"),
        ],
    )

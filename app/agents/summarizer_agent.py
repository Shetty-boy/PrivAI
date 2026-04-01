"""
Summarizer routing agent.
"""
from app.agents.agent_result import AgentExecutionResult, AgentTraceStep


def handle_summarize_request(message: str, session_id: str = "default") -> AgentExecutionResult:
    del message, session_id
    return AgentExecutionResult(
        reply=(
            "To summarize a file, please upload it using the **Summarizer** tab. "
            "You can choose concise, standard, or detailed output there."
        ),
        agent_name="summarizer_agent",
        agent_display_name="Summarizer Agent",
        handoff_trace=[
            AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to summarizer guidance"),
            AgentTraceStep(stage="execution", agent="summarizer_agent", detail="Directed user to summarizer workflow"),
        ],
    )

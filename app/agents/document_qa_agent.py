"""
Document question-answering agent.
"""
from app.agents.agent_result import AgentExecutionResult, AgentTraceStep
from app.tools.rag_engine import answer_query


def handle_document_query(message: str, session_id: str = "default") -> AgentExecutionResult:
    del session_id
    try:
        answer = answer_query(message)
        return AgentExecutionResult(
            reply=f"**From your documents:**\n\n{answer}",
            agent_name="document_qa_agent",
            agent_display_name="Document QA Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to document search"),
                AgentTraceStep(stage="execution", agent="document_qa_agent", detail="Answered using indexed documents"),
            ],
        )
    except Exception as exc:
        return AgentExecutionResult(
            reply=(
                "No documents found to search. Please upload and index documents in the **Documents** tab first.\n\n"
                f"Error: {str(exc)}"
            ),
            agent_name="document_qa_agent",
            agent_display_name="Document QA Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to document search"),
                AgentTraceStep(stage="execution", agent="document_qa_agent", detail="Document search failed"),
            ],
        )

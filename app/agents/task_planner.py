"""
Agent orchestrator that routes detected intents to specialist agents.
"""
from app.agents.agent_result import AgentExecutionResult, AgentTraceStep
from app.agents.document_qa_agent import handle_document_query
from app.agents.general_chat_agent import handle_general_chat
from app.agents.scheduler_agent import handle_schedule_request
from app.agents.summarizer_agent import handle_summarize_request
from app.agents.task_manager_agent import handle_delete_task_request, handle_list_tasks_request

AGENT_REGISTRY = {
    "schedule": handle_schedule_request,
    "query_document": handle_document_query,
    "list_tasks": handle_list_tasks_request,
    "delete_task": handle_delete_task_request,
    "summarize": handle_summarize_request,
    "general_chat": handle_general_chat,
}


def plan_and_execute(message: str, intent: str, session_id: str = "default") -> AgentExecutionResult:
    """
    Route the user request to the appropriate specialist agent.
    """
    handler = AGENT_REGISTRY.get(intent, handle_general_chat)
    result = handler(message=message, session_id=session_id)
    coordinator_step = AgentTraceStep(
        stage="intent",
        agent="intent_detector",
        detail=f"Detected intent: {intent}",
    )
    return AgentExecutionResult(
        reply=result.reply,
        agent_name=result.agent_name,
        agent_display_name=result.agent_display_name,
        handoff_trace=[coordinator_step, *result.handoff_trace],
    )

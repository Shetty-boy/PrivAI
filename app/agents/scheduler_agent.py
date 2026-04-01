"""
Scheduling agent for creating tasks from natural language.
"""
from app.agents.agent_result import AgentExecutionResult, AgentTraceStep
from app.tools.scheduler import create_task


def handle_schedule_request(message: str, session_id: str = "default") -> AgentExecutionResult:
    del session_id
    try:
        task = create_task(message)
        due = task.get("due_date", "No due date")
        due_time = task.get("due_time", "")
        priority = task.get("priority", "medium")
        task_name = task.get("task", "Task")
        time_str = f" at {due_time}" if due_time else ""
        return AgentExecutionResult(
            reply=(
                f"Task created.\n\n"
                f"**Task:** {task_name}\n"
                f"**Due:** {due}{time_str}\n"
                f"**Priority:** {priority.capitalize()}\n\n"
                f"You can edit it anytime in the **Tasks** tab."
            ),
            agent_name="scheduler_agent",
            agent_display_name="Scheduler Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to task creation"),
                AgentTraceStep(stage="execution", agent="scheduler_agent", detail="Parsed natural language into a task"),
            ],
        )
    except Exception as exc:
        return AgentExecutionResult(
            reply=f"I couldn't create that task. Please try the **Tasks** tab directly. Error: {str(exc)}",
            agent_name="scheduler_agent",
            agent_display_name="Scheduler Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to task creation"),
                AgentTraceStep(stage="execution", agent="scheduler_agent", detail="Task creation failed"),
            ],
        )

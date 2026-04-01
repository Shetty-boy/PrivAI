"""
Task management agent for listing and deleting tasks.
"""
from app.agents.agent_result import AgentExecutionResult, AgentTraceStep
from app.tools.scheduler import delete_task_by_name, get_all_tasks


def handle_list_tasks_request(message: str, session_id: str = "default") -> AgentExecutionResult:
    del message, session_id
    try:
        tasks = get_all_tasks()
        if not tasks:
            return AgentExecutionResult(
                reply="You have no tasks yet. Say something like *'Remind me to submit the report by Friday'* to add one.",
                agent_name="task_manager_agent",
                agent_display_name="Task Manager Agent",
                handoff_trace=[
                    AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to task listing"),
                    AgentTraceStep(stage="execution", agent="task_manager_agent", detail="No tasks found"),
                ],
            )

        lines = ["**Your Tasks:**\n"]
        for task in tasks:
            status_icon = "Done" if task["status"] == "done" else "Pending"
            due = task.get("due_date", "—")
            lines.append(
                f"- {status_icon}: **{task['task']}** | Due: {due} | Priority: {task.get('priority', 'medium')}"
            )

        return AgentExecutionResult(
            reply="\n".join(lines),
            agent_name="task_manager_agent",
            agent_display_name="Task Manager Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to task listing"),
                AgentTraceStep(stage="execution", agent="task_manager_agent", detail=f"Returned {len(tasks)} task(s)"),
            ],
        )
    except Exception as exc:
        return AgentExecutionResult(
            reply=f"Couldn't fetch tasks: {str(exc)}",
            agent_name="task_manager_agent",
            agent_display_name="Task Manager Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to task listing"),
                AgentTraceStep(stage="execution", agent="task_manager_agent", detail="Task fetch failed"),
            ],
        )


def handle_delete_task_request(message: str, session_id: str = "default") -> AgentExecutionResult:
    del session_id
    try:
        result = delete_task_by_name(message)
        if result:
            reply = f"Done. I've removed the task: **{result}**"
            detail = "Deleted a matching task"
        else:
            reply = "I couldn't find a matching task. Check the **Tasks** tab to manage tasks directly."
            detail = "No matching task found"

        return AgentExecutionResult(
            reply=reply,
            agent_name="task_manager_agent",
            agent_display_name="Task Manager Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to task deletion"),
                AgentTraceStep(stage="execution", agent="task_manager_agent", detail=detail),
            ],
        )
    except Exception as exc:
        return AgentExecutionResult(
            reply=f"Couldn't delete task: {str(exc)}",
            agent_name="task_manager_agent",
            agent_display_name="Task Manager Agent",
            handoff_trace=[
                AgentTraceStep(stage="routing", agent="coordinator", detail="Routed to task deletion"),
                AgentTraceStep(stage="execution", agent="task_manager_agent", detail="Task deletion failed"),
            ],
        )

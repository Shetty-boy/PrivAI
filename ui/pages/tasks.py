"""
Tasks page for creating, listing, editing, completing, and deleting tasks.
"""
import httpx
import streamlit as st

from app.config import API_HOST, API_PORT

API_BASE = f"http://{API_HOST}:{API_PORT}"

PRIORITY_CONFIG = {
    "high": {"label": "High"},
    "medium": {"label": "Medium"},
    "low": {"label": "Low"},
}


def render_tasks_page():
    st.markdown(
        """
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">Task Manager</h1>
    <p style="color:#94a3b8; margin-bottom:1.5rem;">
        Create tasks with natural language. Your schedule stays private on your device.
    </p>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### Add New Task")
    st.markdown(
        """
    <div class="card">
    <p style="color:#94a3b8; font-size:0.85rem; margin:0 0 0.5rem 0;">
    Try: <em>"Submit the report on Monday at 5pm high priority"</em>
    </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([5, 1])
    with col1:
        task_input = st.text_input(
            "Describe your task in plain English",
            placeholder="e.g. Prepare project presentation slides for Monday",
            label_visibility="collapsed",
        )
    with col2:
        add_btn = st.button("Add", use_container_width=True, type="primary", key="add_task_btn")

    if add_btn and task_input.strip():
        with st.spinner("Parsing task with AI..."):
            try:
                resp = httpx.post(
                    f"{API_BASE}/tasks/create",
                    json={"text": task_input},
                    timeout=60,
                )
                if resp.status_code == 200:
                    task = resp.json()
                    st.success(
                        f"Task added: **{task.get('task')}** | Due: {task.get('due_date', '—')} | "
                        f"Priority: {task.get('priority', 'medium').capitalize()}"
                    )
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
            except httpx.ConnectError:
                st.error("Backend not running.")
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    st.markdown("### Your Tasks")

    tab_all, tab_pending, tab_done = st.tabs(["All Tasks", "Pending", "Done"])

    try:
        resp = httpx.get(f"{API_BASE}/tasks", timeout=10)
        all_tasks = resp.json() if resp.status_code == 200 else []
    except Exception:
        all_tasks = []
        st.error("Could not load tasks. Is the backend running?")

    pending_tasks = [task for task in all_tasks if task.get("status") == "pending"]
    done_tasks = [task for task in all_tasks if task.get("status") == "done"]

    with tab_all:
        if not all_tasks:
            st.info("No tasks yet. Add one above.")
        else:
            _render_task_list(all_tasks, key_prefix="all")

    with tab_pending:
        if not pending_tasks:
            st.success("All caught up. No pending tasks.")
        else:
            _render_task_list(pending_tasks, key_prefix="pending")

    with tab_done:
        if not done_tasks:
            st.info("No completed tasks yet.")
        else:
            _render_task_list(done_tasks, show_done_btn=False, key_prefix="done")

    if all_tasks:
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", len(all_tasks))
        col2.metric("Pending", len(pending_tasks))
        col3.metric("Done", len(done_tasks))


def _render_task_list(tasks: list, show_done_btn: bool = True, key_prefix: str = "tasks"):
    for task in tasks:
        priority = task.get("priority", "medium")
        status = task.get("status", "pending")
        status_label = "Done" if status == "done" else "Pending"
        due_date = task.get("due_date") or "No due date"
        due_time = task.get("due_time")
        due_text = f"{due_date} at {due_time}" if due_time else due_date

        with st.container():
            info_col, done_col, edit_col, del_col = st.columns([7, 1, 1, 1])

            with info_col:
                st.markdown(f"**{task.get('task', 'Task')}**")
                meta_parts = [
                    f"Status: {status_label}",
                    f"Due: {due_text}",
                    f"Priority: {PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG['medium'])['label']}",
                ]
                st.caption(" | ".join(meta_parts))

            with done_col:
                if show_done_btn and status != "done":
                    if st.button(
                        "Done",
                        key=f"{key_prefix}_done_{task['id']}",
                        help="Mark as done",
                        use_container_width=True,
                    ):
                        httpx.patch(f"{API_BASE}/tasks/{task['id']}/done", timeout=10)
                        st.rerun()

            with edit_col:
                if st.button(
                    "Edit",
                    key=f"{key_prefix}_edit_toggle_{task['id']}",
                    help="Edit task",
                    use_container_width=True,
                ):
                    toggle_key = f"edit_open_{task['id']}"
                    st.session_state[toggle_key] = not st.session_state.get(toggle_key, False)
                    st.rerun()

            with del_col:
                if st.button(
                    "Delete",
                    key=f"{key_prefix}_del_{task['id']}",
                    help="Delete task",
                    use_container_width=True,
                ):
                    httpx.delete(f"{API_BASE}/tasks/{task['id']}", timeout=10)
                    st.rerun()

            if st.session_state.get(f"edit_open_{task['id']}", False):
                _render_edit_form(task, key_prefix)

            st.markdown("---")


def _render_edit_form(task: dict, key_prefix: str):
    with st.form(key=f"{key_prefix}_edit_form_{task['id']}"):
        task_name = st.text_input("Task", value=task.get("task", ""))

        col1, col2, col3 = st.columns(3)
        with col1:
            due_date = st.text_input(
                "Due date",
                value=task.get("due_date") or "",
                help="Use YYYY-MM-DD or leave blank.",
            )
        with col2:
            due_time = st.text_input(
                "Due time",
                value=task.get("due_time") or "",
                help="Use HH:MM or leave blank.",
            )
        with col3:
            priority = st.selectbox(
                "Priority",
                options=["low", "medium", "high"],
                index=["low", "medium", "high"].index(task.get("priority", "medium")),
            )

        status = st.selectbox(
            "Status",
            options=["pending", "done"],
            index=["pending", "done"].index(task.get("status", "pending")),
        )

        save_col, cancel_col = st.columns(2)
        save = save_col.form_submit_button("Save changes", use_container_width=True)
        cancel = cancel_col.form_submit_button("Cancel", use_container_width=True)

        if save:
            payload = {
                "task": task_name.strip(),
                "due_date": due_date.strip() or None,
                "due_time": due_time.strip() or None,
                "priority": priority,
                "status": status,
            }
            resp = httpx.patch(f"{API_BASE}/tasks/{task['id']}", json=payload, timeout=15)
            if resp.status_code == 200:
                st.session_state[f"edit_open_{task['id']}"] = False
                st.rerun()
            st.error(f"Could not update task: {resp.text}")

        if cancel:
            st.session_state[f"edit_open_{task['id']}"] = False
            st.rerun()

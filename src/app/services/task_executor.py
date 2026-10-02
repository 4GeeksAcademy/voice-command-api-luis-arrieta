from typing import Any
from fastapi import HTTPException, status

from src.app.api.routes.tasks import (
    create_task,
    delete_task,
    get_tasks,
    replace_task,
    update_task,
)
from src.app.schemas.voice import InstructionPayload, TaskCreate, TaskReplace, TaskUpdate


def execute_instruction(instruction: InstructionPayload) -> Any:
    endpoint = instruction.endpoint.strip()
    method = instruction.method.upper()
    params = instruction.params or {}

    if endpoint == "/tasks":
        if method == "GET":
            return get_tasks()
        elif method == "POST":
            title = str(params.get("title", "")).strip()
            if not title:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Title is required to create a task.",
                )
            done = bool(params.get("done", False))
            return create_task(TaskCreate(title=title, done=done))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Method {method} not allowed for endpoint {endpoint}.",
            )

    parts = [p for p in endpoint.split("/") if p]
    if len(parts) == 2 and parts[0] == "tasks" and parts[1].isdigit():
        task_id = int(parts[1])

        if method == "PUT":
            title = str(params.get("title", "")).strip()
            if not title:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Title is required to replace a task.",
                )
            done = bool(params.get("done", False))
            return replace_task(task_id, TaskReplace(title=title, done=done))
        elif method == "PATCH":
            title_val = params.get("title")
            title = str(title_val).strip() if title_val is not None else None
            done_val = params.get("done")
            done = bool(done_val) if done_val is not None else None
            return update_task(task_id, TaskUpdate(title=title, done=done))
        elif method == "DELETE":
            return delete_task(task_id)
        elif method == "GET":
            # If user asks for a specific task GET /tasks/{id}, return from tasks list or 404
            all_tasks = get_tasks()
            for task in all_tasks:
                if task["id"] == task_id:
                    return task
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Method {method} not allowed for endpoint {endpoint}.",
            )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid or unsupported endpoint '{endpoint}'.",
    )

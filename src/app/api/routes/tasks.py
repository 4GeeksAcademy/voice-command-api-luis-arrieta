from typing import Any
from fastapi import APIRouter, HTTPException, status

from src.app.schemas.voice import Task, TaskCreate, TaskReplace, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Module-level list to store tasks in memory
tasks: list[dict[str, Any]] = []
_next_id: int = 1


def _get_next_id() -> int:
    global _next_id
    current_id = _next_id
    _next_id += 1
    return current_id


def _find_task_index(task_id: int) -> int | None:
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            return index
    return None


@router.get("", response_model=list[Task])
def get_tasks() -> list[dict[str, Any]]:
    return tasks


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> dict[str, Any]:
    new_task = {
        "id": _get_next_id(),
        "title": payload.title,
        "done": payload.done,
    }
    tasks.append(new_task)
    return new_task


@router.put("/{task_id}", response_model=Task)
def replace_task(
    task_id: int,
    payload: TaskReplace,
) -> dict[str, Any]:
    index = _find_task_index(task_id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    updated_task = {
        "id": task_id,
        "title": payload.title,
        "done": payload.done,
    }
    tasks[index] = updated_task
    return updated_task


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    payload: TaskUpdate,
) -> dict[str, Any]:
    index = _find_task_index(task_id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    task = tasks[index]
    update_data = payload.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"] is not None:
        task["title"] = update_data["title"]
    if "done" in update_data and update_data["done"] is not None:
        task["done"] = update_data["done"]

    return task


@router.delete("/{task_id}")
def delete_task(task_id: int) -> dict[str, str]:
    index = _find_task_index(task_id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    tasks.pop(index)
    return {"detail": f"Task {task_id} deleted successfully"}


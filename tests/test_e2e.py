from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.app.api.routes.tasks import tasks
from src.app.schemas.voice import InstructionPayload

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    tasks.clear()
    import src.app.api.routes.tasks as tasks_module
    tasks_module._next_id = 1
    yield
    tasks.clear()
    tasks_module._next_id = 1


def test_cors_preflight_and_headers():
    response = client.options(
        "/tasks",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


@patch("src.app.api.routes.transcribe.parse_instruction_from_groq")
def test_full_e2e_voice_command_cycle(mock_parse):
    # Step 1: Create a task ("Agregar comprar leche")
    mock_parse.return_value = InstructionPayload(
        endpoint="/tasks",
        method="POST",
        params={"title": "Comprar leche", "done": False},
    )

    create_res = client.post("/transcribe", json={"transcription": "Agregar comprar leche"})
    assert create_res.status_code == 200
    create_data = create_res.json()
    assert create_data["transcription"] == "Agregar comprar leche"
    assert create_data["instruction"]["endpoint"] == "/tasks"
    assert create_data["instruction"]["method"] == "POST"
    assert create_data["result"]["id"] == 1
    assert create_data["result"]["title"] == "Comprar leche"
    assert create_data["result"]["done"] is False

    # Step 2: List tasks ("Mostrar mis tareas")
    mock_parse.return_value = InstructionPayload(
        endpoint="/tasks",
        method="GET",
        params={},
    )

    list_res = client.post("/transcribe", json={"transcription": "Mostrar mis tareas"})
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["transcription"] == "Mostrar mis tareas"
    assert len(list_data["result"]) == 1
    assert list_data["result"][0]["id"] == 1

    # Step 3: Update a task ("Marcar tarea 1 como completada")
    mock_parse.return_value = InstructionPayload(
        endpoint="/tasks/1",
        method="PATCH",
        params={"done": True},
    )

    update_res = client.post("/transcribe", json={"transcription": "Marcar tarea 1 como completada"})
    assert update_res.status_code == 200
    update_data = update_res.json()
    assert update_data["instruction"]["endpoint"] == "/tasks/1"
    assert update_data["instruction"]["method"] == "PATCH"
    assert update_data["result"]["id"] == 1
    assert update_data["result"]["done"] is True

    # Step 4: Delete a task ("Eliminar la tarea 1")
    mock_parse.return_value = InstructionPayload(
        endpoint="/tasks/1",
        method="DELETE",
        params={},
    )

    delete_res = client.post("/transcribe", json={"transcription": "Eliminar la tarea 1"})
    assert delete_res.status_code == 200
    delete_data = delete_res.json()
    assert delete_data["instruction"]["endpoint"] == "/tasks/1"
    assert delete_data["instruction"]["method"] == "DELETE"
    assert "deleted successfully" in delete_data["result"]["detail"]

    # Verify task list is empty after deletion
    mock_parse.return_value = InstructionPayload(
        endpoint="/tasks",
        method="GET",
        params={},
    )
    final_list_res = client.post("/transcribe", json={"transcription": "Ver tareas"})
    assert final_list_res.json()["result"] == []

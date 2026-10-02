from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.app.api.routes.tasks import tasks
from src.app.schemas.voice import InstructionPayload

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_tasks():
    tasks.clear()
    import src.app.api.routes.tasks as tasks_module
    tasks_module._next_id = 1
    yield
    tasks.clear()
    tasks_module._next_id = 1


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("src.app.api.routes.transcribe.parse_instruction_from_groq")
def test_transcribe_manual_json_flow(mock_parse):
    mock_parse.return_value = InstructionPayload(
        endpoint="/tasks",
        method="POST",
        params={"title": "Comprar manzanas"},
    )

    response = client.post(
        "/transcribe",
        json={"transcription": "Agregar comprar manzanas"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["transcription"] == "Agregar comprar manzanas"
    assert data["instruction"]["endpoint"] == "/tasks"
    assert data["instruction"]["method"] == "POST"
    assert data["result"]["id"] == 1
    assert data["result"]["title"] == "Comprar manzanas"
    assert data["result"]["done"] is False
    assert len(tasks) == 1


@patch("src.app.api.routes.transcribe.transcribe_audio_with_groq")
@patch("src.app.api.routes.transcribe.parse_instruction_from_groq")
def test_transcribe_audio_file_flow(mock_parse, mock_transcribe_audio):
    mock_transcribe_audio.return_value = "Mostrar mis tareas"
    mock_parse.return_value = InstructionPayload(
        endpoint="/tasks",
        method="GET",
        params={},
    )

    fake_audio_bytes = b"OggS_fake_audio_data"
    files = {"file": ("audio.webm", fake_audio_bytes, "audio/webm")}
    data = {"language": "es"}

    response = client.post("/transcribe", files=files, data=data)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["transcription"] == "Mostrar mis tareas"
    assert res_data["instruction"]["endpoint"] == "/tasks"
    assert res_data["instruction"]["method"] == "GET"
    assert res_data["result"] == []


def test_transcribe_empty_transcription():
    response = client.post("/transcribe", json={"transcription": "   "})
    assert response.status_code == 400


def test_transcribe_invalid_json():
    response = client.post(
        "/transcribe",
        headers={"Content-Type": "application/json"},
        content="not a json",
    )
    assert response.status_code == 400

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from groq import GroqError

from src.main import app
from src.app.services.groq_service import validate_and_sanitize_instruction
from src.app.schemas.voice import InstructionPayload

client = TestClient(app)


def test_validate_and_sanitize_valid_post():
    data = {
        "endpoint": "/tasks",
        "method": "POST",
        "params": {"title": "Comprar leche"},
    }
    result = validate_and_sanitize_instruction(data)
    assert isinstance(result, InstructionPayload)
    assert result.endpoint == "/tasks"
    assert result.method == "POST"
    assert result.params == {"title": "Comprar leche"}


def test_validate_and_sanitize_valid_patch():
    data = {
        "endpoint": "/tasks/5",
        "method": "patch",
        "params": {"done": True},
    }
    result = validate_and_sanitize_instruction(data)
    assert result.endpoint == "/tasks/5"
    assert result.method == "PATCH"
    assert result.params == {"done": True}


def test_validate_and_sanitize_disallowed_method():
    data = {
        "endpoint": "/tasks",
        "method": "CONNECT",
        "params": {},
    }
    with pytest.raises(Exception) as exc_info:
        validate_and_sanitize_instruction(data)
    assert "Disallowed HTTP method" in str(exc_info.value.detail)


def test_validate_and_sanitize_disallowed_endpoint():
    data = {
        "endpoint": "/users/delete_all",
        "method": "POST",
        "params": {},
    }
    with pytest.raises(Exception) as exc_info:
        validate_and_sanitize_instruction(data)
    assert "Disallowed endpoint" in str(exc_info.value.detail)


@patch("src.app.services.groq_service.Groq")
def test_post_instruction_create_task(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content='{"endpoint": "/tasks", "method": "POST", "params": {"title": "Comprar pan"}}'
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    response = client.post("/instruction", json={"transcription": "Agregar comprar pan"})
    assert response.status_code == 200
    data = response.json()
    assert data["endpoint"] == "/tasks"
    assert data["method"] == "POST"
    assert data["params"] == {"title": "Comprar pan"}


@patch("src.app.services.groq_service.Groq")
def test_post_instruction_delete_task(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content='{"endpoint": "/tasks/3", "method": "DELETE", "params": {}}'
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    response = client.post("/instruction", json={"transcription": "Eliminar la tarea 3"})
    assert response.status_code == 200
    data = response.json()
    assert data["endpoint"] == "/tasks/3"
    assert data["method"] == "DELETE"
    assert data["params"] == {}


@patch("src.app.services.groq_service.Groq")
def test_post_instruction_groq_error(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = GroqError("API rate limit reached")

    response = client.post("/instruction", json={"transcription": "Cualquier cosa"})
    assert response.status_code == 502
    assert "Error communicating with Groq" in response.json()["detail"]

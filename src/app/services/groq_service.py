import json
import re
from typing import Any
from fastapi import HTTPException, status
from groq import Groq, GroqError

from src.app.core.config import get_settings
from src.app.schemas.voice import InstructionPayload

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def transcribe_audio_with_groq(
    file_bytes: bytes,
    filename: str = "audio.webm",
    language: str | None = None,
) -> str:
    settings = get_settings()

    if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Groq API key is not configured.",
        )

    client = Groq(api_key=settings.groq_api_key)

    try:
        kwargs: dict[str, Any] = {
            "file": (filename, file_bytes),
            "model": settings.groq_transcription_model,
            "response_format": "text",
        }
        if language:
            kwargs["language"] = language

        transcription_res = client.audio.transcriptions.create(**kwargs)
        return str(transcription_res).strip()
    except GroqError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error transcribing audio with Groq: {str(exc)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during transcription: {str(exc)}",
        )


def parse_instruction_from_groq(transcription: str) -> InstructionPayload:
    settings = get_settings()

    if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Groq API key is not configured.",
        )

    client = Groq(api_key=settings.groq_api_key)

    system_prompt = (
        "You are an AI assistant that translates natural language task commands into structured HTTP API instructions.\n"
        "Your output MUST be a JSON object with exactly three fields: 'endpoint', 'method', and 'params'.\n\n"
        "Allowed API Endpoints:\n"
        "- GET /tasks : List all tasks. Params: {}\n"
        "- POST /tasks : Create a task. Params: {'title': str, 'done': bool (optional, default false)}\n"
        "- PUT /tasks/{id} : Replace a task by integer ID. Params: {'title': str, 'done': bool}\n"
        "- PATCH /tasks/{id} : Update a task by integer ID. Params: {'title': str (optional), 'done': bool (optional)}\n"
        "- DELETE /tasks/{id} : Delete a task by integer ID. Params: {}\n\n"
        "Examples:\n"
        "Input: 'Agregar comprar leche'\n"
        "Output: {\"endpoint\": \"/tasks\", \"method\": \"POST\", \"params\": {\"title\": \"comprar leche\"}}\n\n"
        "Input: 'Mostrar mis tareas'\n"
        "Output: {\"endpoint\": \"/tasks\", \"method\": \"GET\", \"params\": {}}\n\n"
        "Input: 'Marcar la tarea 1 como completada'\n"
        "Output: {\"endpoint\": \"/tasks/1\", \"method\": \"PATCH\", \"params\": {\"done\": true}}\n\n"
        "Input: 'Eliminar tarea 2'\n"
        "Output: {\"endpoint\": \"/tasks/2\", \"method\": \"DELETE\", \"params\": {}}\n\n"
        "Return strictly valid JSON only. Do not wrap in markdown or backticks."
    )

    try:
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcription},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content or ""
    except GroqError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error communicating with Groq LLM provider: {str(exc)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error calling Groq: {str(exc)}",
        )

    try:
        data = json.loads(content.strip())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq LLM returned an invalid JSON response.",
        )

    return validate_and_sanitize_instruction(data)


def validate_and_sanitize_instruction(data: dict[str, Any]) -> InstructionPayload:
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="LLM output is not a JSON object.",
        )

    endpoint = data.get("endpoint")
    method = data.get("method")
    params = data.get("params")

    if not isinstance(endpoint, str) or not isinstance(method, str) or not isinstance(params, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="LLM output missing required fields ('endpoint', 'method', 'params').",
        )

    method_upper = method.upper()
    if method_upper not in ALLOWED_METHODS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Disallowed HTTP method '{method}' returned by LLM.",
        )

    clean_endpoint = endpoint.strip()
    if not (clean_endpoint == "/tasks" or re.match(r"^/tasks/\d+$", clean_endpoint)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Disallowed endpoint '{clean_endpoint}' returned by LLM.",
        )

    return InstructionPayload(
        endpoint=clean_endpoint,
        method=method_upper,
        params=params,
    )

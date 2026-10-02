from fastapi import APIRouter, HTTPException, Request, status

from src.app.schemas.voice import TranscribeFlowResponse
from src.app.services.groq_service import (
    parse_instruction_from_groq,
    transcribe_audio_with_groq,
)
from src.app.services.task_executor import execute_instruction

router = APIRouter(tags=["transcribe"])


@router.get("/")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/transcribe", response_model=TranscribeFlowResponse)
async def transcribe_and_run_flow(request: Request) -> TranscribeFlowResponse:
    content_type = request.headers.get("content-type", "").lower()
    transcription = ""

    if "multipart/form-data" in content_type:
        form = await request.form()
        audio_file = form.get("file")
        language_val = form.get("language")
        language = str(language_val).strip() if language_val else None

        if not audio_file or not hasattr(audio_file, "read"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing audio file in form data under key 'file'.",
            )

        file_bytes = await audio_file.read()
        filename = getattr(audio_file, "filename", "audio.webm") or "audio.webm"
        transcription = transcribe_audio_with_groq(
            file_bytes, filename=filename, language=language
        )

    elif "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload.",
            )

        if not isinstance(data, dict) or "transcription" not in data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="JSON payload must contain 'transcription' field.",
            )

        transcription = str(data["transcription"]).strip()

    else:
        try:
            data = await request.json()
            if isinstance(data, dict) and "transcription" in data:
                transcription = str(data["transcription"]).strip()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported Content-Type '{content_type}'. Expected application/json or multipart/form-data.",
            )

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcription text cannot be empty.",
        )

    instruction = parse_instruction_from_groq(transcription)
    result = execute_instruction(instruction)

    return TranscribeFlowResponse(
        transcription=transcription,
        instruction=instruction,
        result=result,
    )

# Voice Command API at 4Geeks Academy

<!-- hide -->

By [@ehiber](https://github.com/ehiber) and [other contributors](https://github.com/4GeeksAcademy/voice-command-api/graphs/contributors) at [4Geeks Academy](https://4geeksacademy.com/)

[![build by developers](https://img.shields.io/badge/build_by-Developers-blue)](https://4geeks.com)
[![4Geeks Academy](https://img.shields.io/twitter/follow/4geeksacademy?style=social&logo=x)](https://x.com/4geeksacademy)

_Estas instrucciones también están disponibles en [español](./README.es.md)._

**Before you start**: Read the [how to start a coding project](https://4geeks.com/lesson/how-to-start-a-project) guide before writing code.

> We need you! These exercises are built and maintained in collaboration with people like you. If you find any bug 🐞 or typo, please contribute and/or report it.

<!-- endhide -->

---

## 🎯 Project Overview

This repository contains the completed **Voice Command API** backend project.

The frontend records up to **20 seconds** of audio in the browser, sends that audio to your backend API, and displays:

- the transcription returned by the API
- the structured routing instruction payload
- the final task response returned by the API

---

## How the project works

The frontend uses a single public entry point:

- `POST /transcribe`

That endpoint:

1. receives recorded audio (or text in manual fallback mode)
2. transcribes audio to text via Groq Whisper (`whisper-large-v3-turbo`)
3. reuses the routing logic from `POST /instruction` via Groq (`llama-3.1-8b-instant`)
4. executes the corresponding task action in memory
5. returns the transcription, instruction payload, and final result

The backend exposes all required endpoints:

- `POST /instruction`
- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

---

## Repository structure

```text
voice-command-api/
|-- .devcontainer/           # Codespaces setup
|-- frontend/                # Vite/TypeScript frontend
|   |-- public/
|   `-- src/
|-- src/
|   `-- app/
|       |-- api/routes/      # /transcribe, /instruction, /tasks
|       |-- core/            # Settings and config
|       |-- schemas/         # Pydantic request/response contracts
|       |-- services/        # Groq integration & task executor
|       `-- utils/
|-- tests/                   # Pytest test suite
|-- pyproject.toml
|-- README.md
`-- README.es.md
```

---

## 🌱 How to run the project

### Backend setup

1. Create `.env` from `.env.example` and fill in your Groq API credentials:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TRANSCRIPTION_MODEL=whisper-large-v3-turbo
REQUEST_TIMEOUT_SECONDS=45
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

2. Install dependencies and start the API:

```bash
uv sync
uv run uvicorn src.main:app --reload
```
*(Or with your virtual environment: `.venv/Scripts/python -m uvicorn src.main:app --reload`)*

### Frontend setup

1. Create `frontend/.env` from `frontend/.env.example`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

2. Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 How to run the test suite

To run the complete unit and integration test suite (24 tests total):

```bash
python -m pytest
```

---

## 💻 Completed Requirements Checklist

- [x] Module-level `tasks` list with `id`, `title`, and `done`, using unique incremental IDs.
- [x] Implemented `GET /tasks`, `POST /tasks`, `PUT /tasks/{task_id}`, `PATCH /tasks/{task_id}`, and `DELETE /tasks/{task_id}` using in-memory state.
- [x] Implemented `POST /instruction` to receive `{ "transcription": "..." }`, call Groq, and return **only** routing JSON (no action execution).
- [x] Implemented `POST /transcribe` to accept `multipart/form-data` and `application/json`, convert audio/text, reuse `/instruction` logic, execute the action, and return `transcription`, `instruction`, and `result`.
- [x] Intent routing is performed dynamically by Groq LLM without hardcoded keyword rules.

---

## ✅ Evaluation Criteria

- [x] `POST /transcribe` accepts audio, transcribes it, and reuses `/instruction` routing logic.
- [x] `POST /instruction` receives plain text and returns only routing JSON (no action execution).
- [x] `GET /tasks`, `POST /tasks`, `PUT /tasks/{task_id}`, `PATCH /tasks/{task_id}`, and `DELETE /tasks/{task_id}` work correctly with in-memory state.
- [x] The frontend displays the transcription returned by the backend to help distinguish STT errors from routing errors.

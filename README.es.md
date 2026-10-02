# Voice Command API en 4Geeks Academy

<!-- hide -->

Por [@ehiber](https://github.com/ehiber) y [otros contribuidores](https://github.com/4GeeksAcademy/voice-command-api/graphs/contributors) en [4Geeks Academy](https://4geeksacademy.com/)

[![build by developers](https://img.shields.io/badge/build_by-Developers-blue)](https://4geeks.com)
[![4Geeks Academy](https://img.shields.io/twitter/follow/4geeksacademy?style=social&logo=x)](https://x.com/4geeksacademy)

_These instructions are also available in [English](./README.md)._

**Antes de empezar**: Lee la guia de [como comenzar un proyecto de programacion](https://4geeks.com/lesson/how-to-start-a-project) antes de escribir codigo.

> ¡Te necesitamos! Estos ejercicios se construyen y mantienen en colaboracion con personas como tu. Si encuentras algun error 🐞 o falta de ortografia, por favor contribuye y/o reportalo.

<!-- endhide -->

---

## 🎯 Tu reto

Este repositorio contiene la implementación completada del proyecto **Voice Command API**.

El frontend está integrado para grabar hasta **20 segundos** de audio en el navegador, enviar ese audio a tu backend y mostrar:

- la transcripción devuelta por la API
- la instrucción estructurada de enrutamiento
- la respuesta final de tareas devuelta por la API

---

## Cómo funciona el proyecto

El frontend usa un único punto de entrada público:

- `POST /transcribe`

Este endpoint:

1. recibe el audio grabado desde el frontend (o texto en fallback manual)
2. transcribe el audio a texto usando Groq Whisper (`whisper-large-v3-turbo`)
3. reutiliza la misma lógica de routing de `POST /instruction` con Groq (`llama-3.1-8b-instant`)
4. ejecuta la acción correspondiente sobre las tareas en memoria
5. devuelve la transcripción, la instrucción y el resultado final

La API expone todos los endpoints requeridos:

- `POST /instruction`
- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

---

## Estructura del repositorio

```text
voice-command-api/
|-- .devcontainer/           # Configuración para Codespaces
|-- frontend/                # Frontend en Vite/TypeScript
|   |-- public/
|   `-- src/
|-- src/
|   `-- app/
|       |-- api/routes/      # /transcribe, /instruction, /tasks
|       |-- core/            # Configuración y settings
|       |-- schemas/         # Contratos Pydantic
|       |-- services/        # Integración Groq y ejecutor de tareas
|       `-- utils/
|-- tests/                   # Suite completa de pruebas pytest
|-- pyproject.toml
|-- README.md
`-- README.es.md
```

---

## 🌱 Cómo iniciar el proyecto

### Configuración del backend

1. Crea un archivo `.env` a partir de `.env.example` y agrega tus credenciales de Groq:

```env
GROQ_API_KEY=tu_groq_api_key_aqui
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TRANSCRIPTION_MODEL=whisper-large-v3-turbo
REQUEST_TIMEOUT_SECONDS=45
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

2. Instala dependencias y ejecuta la API:

```bash
uv sync
uv run uvicorn src.main:app --reload
```
*(O utilizando tu entorno virtual: `.venv/Scripts/python -m uvicorn src.main:app --reload`)*

### Configuración del frontend

1. Crea `frontend/.env` a partir de `frontend/.env.example`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

2. Ejecuta el frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Cómo ejecutar la suite de pruebas

Para correr las pruebas unitarias e integradas (24 pruebas en total):

```bash
python -m pytest
```

---

## 💻 Checklist de implementación cumplida

- [x] Lista `tasks` a nivel de módulo con `id`, `title` y `done`, usando IDs únicos e incrementales.
- [x] Endpoints `GET /tasks`, `POST /tasks`, `PUT /tasks/{task_id}`, `PATCH /tasks/{task_id}` y `DELETE /tasks/{task_id}` con almacenamiento en memoria.
- [x] Endpoint `POST /instruction` para recibir `{ "transcription": "..." }`, llamar a Groq y devolver **solo** JSON de routing (sin ejecutar tareas).
- [x] Endpoint `POST /transcribe` para aceptar `multipart/form-data` y `application/json`, convertir audio/texto, reutilizar la lógica de `/instruction`, ejecutar la acción y devolver `transcription`, `instruction` y `result`.
- [x] Sin lógica manual rígida de coincidencia de intenciones tipo `if "add" in text`. La interpretación es responsabilidad del modelo LLM.

---

## ✅ Evaluación

- [x] `POST /transcribe` recibe audio, transcribe y reutiliza la lógica de `/instruction`.
- [x] `POST /instruction` recibe texto plano y devuelve solo JSON de routing (sin ejecutar acciones).
- [x] `GET /tasks`, `POST /tasks`, `PUT /tasks/{task_id}`, `PATCH /tasks/{task_id}` y `DELETE /tasks/{task_id}` funcionan correctamente con memoria en proceso.
- [x] El frontend muestra la transcripción devuelta por el backend para distinguir errores de STT vs. errores de routing.

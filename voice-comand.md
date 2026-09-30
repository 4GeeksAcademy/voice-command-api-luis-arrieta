# Voice Command API — Habla con tu Lista de Tareas

Guía de trabajo basada en el enunciado oficial de 4Geeks. El archivo conserva el nombre solicitado (`voice-comand.md`); `comand` aparece escrito con una sola **m**.

- **Cohorte:** Backend development with Coding Agents (`1670`)
- **Tarea 4Geeks:** `1000151` — *Voice Command API - Talk to Your Task List*
- **Estado consultado:** `PENDING`
- **Repositorio de partida del ejercicio:** [4GeeksAcademy/voice-command-api](https://github.com/4GeeksAcademy/voice-command-api)
- **Enunciado oficial:** [README en español](https://github.com/4GeeksAcademy/ai-engineering-syllabus/blob/main/content/projects/voice-to-do-list-api/README.es.md) · [README en inglés](https://github.com/4GeeksAcademy/ai-engineering-syllabus/blob/main/content/projects/voice-to-do-list-api/README.md)
- **Alcance:** documentar las instrucciones; el código de la API aún no está implementado por este documento.

> Se autenticó la cuenta con `TOKEN_4GEEKS` desde el `.env` local y se confirmó la tarea `1000151` en la cohorte `1670`, con estado `PENDING`. La clave no se incluye en este documento.

## 1. Objetivo

Construir el backend que conecta la interfaz de voz incluida con una lista de tareas. El navegador ya captura la voz con la Web Speech API y la convierte en texto. El backend debe:

1. Recibir la transcripción en `POST /instruction`.
2. Pedir a Groq que clasifique la intención y produzca una instrucción estructurada.
3. Devolver un JSON que indique el endpoint, método y parámetros de la acción.
4. Permitir que el frontend use esa respuesta para llamar a uno de los endpoints CRUD de tareas.

Flujo esperado: voz → transcripción en el navegador → `/instruction` → JSON de enrutamiento → petición a `/tasks` → resultado visible en la interfaz.

## 2. Repositorio y límites

El enunciado indica que el ejercicio parte del repositorio `4GeeksAcademy/voice-command-api`, que ya contiene:

- `/frontend`: interfaz proporcionada; **no modificarla** como parte del ejercicio.
- `/src`: ubicación prevista para el backend FastAPI.

Crear un fork/repositorio propio siguiendo las instrucciones del curso y trabajar sobre esa base. Este proyecto es una app independiente: no mover el frontend ni el backend al monorepo de Nexova. Este archivo es una guía de requisitos, no sustituye el repo de la tarea ni el README que se debe entregar en la raíz del repo propio.

## 3. Requisitos funcionales

### 3.1 Endpoint de instrucciones

`POST /instruction`

- Recibe JSON con `transcription` (texto transcrito por la interfaz).
- Llama al SDK/API de Groq desde el backend con un prompt de sistema claro.
- Modelo indicado por el enunciado: `llama3-8b-8192` o un modelo equivalente disponible en la cuenta.
- Solicita únicamente un objeto JSON con esta forma:

```json
{
  "endpoint": "/tasks",
  "method": "POST",
  "params": { "title": "Comprar leche" }
}
```

- El JSON representa la acción que el frontend deberá ejecutar después; `/instruction` devuelve la instrucción estructurada, no una respuesta libre del modelo.
- No codificar el reconocimiento de intenciones con reglas como `if "añade" in transcription`. La interpretación de lo que pidió el usuario debe venir del modelo.
- Validar de todas formas la salida recibida de Groq en el servidor: JSON parseable, campos requeridos, método y endpoint entre opciones permitidas, y parámetros con tipos/valores esperados. La respuesta del modelo no es confiable ni debe convertirse en una llamada arbitraria.
- En errores de Groq, timeout, JSON inválido o petición ambigua, devolver un error HTTP/JSON claro; no filtrar la API key ni mensajes internos sensibles.

### 3.2 Endpoints CRUD

Almacenamiento exclusivamente en memoria: una lista Python a nivel de módulo llamada `tasks`. No usar base de datos ni archivos. Se reinicia al reiniciar el proceso, y esa pérdida de datos es intencional para el ejercicio.

Cada tarea tiene:

```json
{ "id": 1, "title": "Comprar leche", "done": false }
```

Endpoints requeridos:

| Método | Ruta FastAPI | Comportamiento |
|---|---|---|
| `GET` | `/tasks` | Devolver todas las tareas como array JSON. |
| `POST` | `/tasks` | Recibir `title` obligatorio y `done` opcional (por defecto `false`); asignar ID único y devolver la tarea creada. |
| `PUT` | `/tasks/{task_id}` | Reemplazar por completo la tarea identificada. Validar el cuerpo completo según el contrato elegido y responder 404 si no existe. |
| `PATCH` | `/tasks/{task_id}` | Actualizar parcialmente `title` y/o `done`, sin alterar campos omitidos; responder 404 si no existe. |
| `DELETE` | `/tasks/{task_id}` | Eliminar la tarea indicada y devolver confirmación; responder 404 si no existe. |

**Nota de sintaxis:** el README expresa algunas rutas con `<int:task_id>`, que es una convención de Flask. En FastAPI se usa típicamente `/tasks/{task_id}` y el tipo entero se declara en la función/parámetro.

Códigos sugeridos: `200` para lecturas/actualizaciones/eliminaciones exitosas, `201` al crear, `404` para ID inexistente y `422` para datos que no pasan la validación automática o definida por la app.

### 3.3 CORS y secretos

- Configurar CORS para permitir que el frontend proporcionado llame a la API. Permitir los orígenes necesarios del entorno de desarrollo; no abrir todos los orígenes sin motivo.
- Crear entorno virtual e instalar FastAPI, Uvicorn y el SDK de Groq, según el README.
- Leer `GROQ_API_KEY` desde un archivo `.env` local o variable de entorno del servidor. Añadir `.env` a `.gitignore`; entregar un `.env.example` sin credenciales si hace falta documentar el nombre.
- No confundir el token de 4Geeks con la API key de Groq: son credenciales distintas. Ninguna debe aparecer en Git, frontend, capturas o logs.

## 4. Requisito extremo a extremo

La interfaz debe completar acciones habladas al menos para:

- crear una tarea;
- listar tareas;
- actualizar una tarea (título o estado completado);
- eliminar una tarea.

Prueba el ciclo completo desde el navegador. No basta con probar `/instruction` aislado: hay que verificar que la respuesta del modelo tenga el formato que el frontend espera y que este realice la llamada de seguimiento correcta.

## 5. Seguridad y robustez de la salida del LLM

La transcripción es entrada externa. La API debe tratar tanto el texto reconocido como la respuesta del modelo como datos no confiables.

- El LLM solo puede seleccionar de una lista cerrada de endpoints/métodos CRUD permitidos; nunca ejecutar código ni construir una URL arbitraria desde la transcripción.
- Validar el verbo HTTP, ruta y parámetros contra esquemas conocidos antes de devolver la acción.
- No incrustar la API key de Groq en JavaScript ni enviarla en respuestas.
- Controlar errores, respuestas vacías y salidas que no sean JSON. No hacer `eval` ni ejecutar texto del modelo.
- Si el usuario no da información suficiente para una acción —por ejemplo, actualizar o borrar sin identificar una tarea— el resultado debe ser una respuesta controlada que la UI pueda presentar, según el contrato disponible del frontend. No inventar IDs.

Estas validaciones no son detección manual de intención: son controles de seguridad y validación de formato. La clasificación semántica sigue siendo trabajo del modelo, de acuerdo con la restricción del enunciado.

## 6. Checklist de aceptación

### Preparación
- [ ] Repo propio basado en `4GeeksAcademy/voice-command-api`.
- [ ] No modificar el frontend suministrado.
- [ ] Backend FastAPI en `/src` y dependencias instaladas en un entorno virtual.
- [ ] `.env` ignorado por Git y clave de Groq solo del lado servidor.
- [ ] CORS permite el origen real del frontend de desarrollo.

### CRUD en memoria
- [ ] Existe una lista a nivel de módulo llamada `tasks`.
- [ ] Cada elemento contiene `id`, `title` y `done` con tipos correctos.
- [ ] GET, POST, PUT, PATCH y DELETE funcionan con JSON y códigos apropiados.
- [ ] Los IDs no se duplican y las operaciones no existentes responden con error claro.
- [ ] Los cambios desaparecen al reiniciar el servidor (comportamiento exigido).

### Voz/LLM
- [ ] `/instruction` recibe `{ "transcription": "..." }`.
- [ ] `/instruction` invoca Groq usando la clave de entorno.
- [ ] El prompt exige exclusivamente JSON en el contrato `endpoint`, `method`, `params`.
- [ ] No existe lógica manual tipo palabra clave → endpoint para interpretar la intención.
- [ ] Se valida la salida del LLM antes de devolverla; errores del proveedor no exponen secretos.
- [ ] El frontend ejecuta correctamente crear, listar, actualizar y borrar a partir de instrucciones habladas.

### Entrega
- [ ] README en la raíz explica instalación, configuración segura, ejecución y pruebas.
- [ ] Repo propio público, según pide el enunciado, y enlace entregado al instructor.
- [ ] Revisar `git status` y el diff para confirmar que `.env`, tokens y credenciales no se incluyen.

## 7. Aclaración del contrato de flujo

El enunciado describe `/instruction` como punto de entrada que determina la acción y también indica explícitamente que el frontend usa la respuesta para hacer una petición de seguimiento. La interpretación para implementar es: **`/instruction` devuelve el objeto de enrutamiento; el frontend realiza luego la operación CRUD**. Así la API no ejecuta dos veces la acción ni hay ambigüedad sobre quién hace el segundo request.

El backend debe mantener el contrato exacto que consuma el frontend ya proporcionado. Antes de cambiar nombres de campos, formato de respuesta o forma de los parámetros, revisar el código del frontend y probar la integración real.

## 8. Fuentes

- [README oficial del proyecto en español](https://github.com/4GeeksAcademy/ai-engineering-syllabus/blob/main/content/projects/voice-to-do-list-api/README.es.md)
- [README oficial del proyecto en inglés](https://github.com/4GeeksAcademy/ai-engineering-syllabus/blob/main/content/projects/voice-to-do-list-api/README.md)
- [Repositorio starter de Voice Command API](https://github.com/4GeeksAcademy/voice-command-api)

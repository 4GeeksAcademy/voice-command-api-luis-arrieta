import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.app.api.routes.tasks import tasks, _next_id

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_tasks():
    global _next_id
    tasks.clear()
    import src.app.api.routes.tasks as tasks_module
    tasks_module._next_id = 1
    yield
    tasks.clear()
    tasks_module._next_id = 1


def test_get_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task_default_done():
    response = client.post("/tasks", json={"title": "Comprar leche"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Comprar leche"
    assert data["done"] is False


def test_create_task_with_done():
    response = client.post("/tasks", json={"title": "Comprar pan", "done": True})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Comprar pan"
    assert data["done"] is True


def test_get_tasks_after_creation():
    client.post("/tasks", json={"title": "Tarea 1"})
    client.post("/tasks", json={"title": "Tarea 2"})

    response = client.get("/tasks")
    assert response.status_code == 200
    tasks_list = response.json()
    assert len(tasks_list) == 2
    assert tasks_list[0]["id"] == 1
    assert tasks_list[1]["id"] == 2


def test_replace_task_success():
    client.post("/tasks", json={"title": "Tarea Original", "done": False})
    response = client.put("/tasks/1", json={"title": "Tarea Reemplazada", "done": True})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Tarea Reemplazada"
    assert data["done"] is True


def test_replace_task_not_found():
    response = client.put("/tasks/999", json={"title": "No existe", "done": True})
    assert response.status_code == 404


def test_patch_task_success():
    client.post("/tasks", json={"title": "Comprar manzana", "done": False})
    
    # Update only done
    response = client.patch("/tasks/1", json={"done": True})
    assert response.status_code == 200
    assert response.json()["done"] is True
    assert response.json()["title"] == "Comprar manzana"

    # Update only title
    response = client.patch("/tasks/1", json={"title": "Comprar pera"})
    assert response.status_code == 200
    assert response.json()["done"] is True
    assert response.json()["title"] == "Comprar pera"


def test_patch_task_not_found():
    response = client.patch("/tasks/999", json={"done": True})
    assert response.status_code == 404


def test_delete_task_success():
    client.post("/tasks", json={"title": "Tarea a borrar"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200

    # Verify deleted
    get_res = client.get("/tasks")
    assert len(get_res.json()) == 0


def test_delete_task_not_found():
    response = client.delete("/tasks/999")
    assert response.status_code == 404


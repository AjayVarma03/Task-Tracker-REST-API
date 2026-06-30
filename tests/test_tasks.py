import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app(test_config={"TESTING": True})
    with app.test_client() as client:
        yield client


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_create_task_success(client):
    resp = client.post("/tasks", json={"title": "Write README", "priority": 2})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write README"
    assert body["status"] == "TODO"
    assert "id" in body


def test_create_task_missing_title(client):
    resp = client.post("/tasks", json={"priority": 2})
    assert resp.status_code == 400
    assert "title" in resp.get_json()["error"]


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B", "status": "DONE"})

    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2

    resp_filtered = client.get("/tasks?status=DONE")
    assert len(resp_filtered.get_json()) == 1
    assert resp_filtered.get_json()[0]["title"] == "Task B"


def test_get_task_not_found(client):
    resp = client.get("/tasks/64b64b64b64b64b64b64b64b")
    assert resp.status_code == 404


def test_get_task_invalid_id(client):
    resp = client.get("/tasks/not-a-valid-id")
    assert resp.status_code == 400


def test_update_task_partial(client):
    create_resp = client.post("/tasks", json={"title": "Old title"})
    task_id = create_resp.get_json()["id"]

    patch_resp = client.patch(f"/tasks/{task_id}", json={"status": "IN_PROGRESS"})
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["status"] == "IN_PROGRESS"
    assert patch_resp.get_json()["title"] == "Old title"


def test_update_task_invalid_status(client):
    create_resp = client.post("/tasks", json={"title": "Task"})
    task_id = create_resp.get_json()["id"]

    patch_resp = client.patch(f"/tasks/{task_id}", json={"status": "NOT_A_STATUS"})
    assert patch_resp.status_code == 400


def test_delete_task(client):
    create_resp = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_resp.get_json()["id"]

    del_resp = client.delete(f"/tasks/{task_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404

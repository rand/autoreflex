from app.models.schemas import TaskRequest

def test_create_and_optimize_flow(client):
    # 1. Optimize (Creates Task + Optimization)
    payload = {
        "description": "Build a react component",
        "context_files": [],
        "constraints": "Must use typescript"
    }
    response = client.post("/api/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["original_task"] == payload["description"]
    assert "optimized_prompt" in data
    assert data["id"] is not None
    task_id = data["id"]

    # 2. Verify History
    response = client.get("/api/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) > 0
    assert history[0]["id"] == task_id
    assert history[0]["status"] == "optimizing"

def test_run_agent_flow(client):
    # 1. Setup: Must optimize first to exist in DB
    setup_payload = {
        "description": "Run this script",
        "context_files": [],
        "constraints": "None"
    }
    setup_resp = client.post("/api/optimize", json=setup_payload)
    assert setup_resp.status_code == 200
    task_id = setup_resp.json()["id"]

    # 2. Start Run using task_id
    run_payload = {"task_id": task_id}
    response = client.post("/api/run", json=run_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert data["task_id"] == task_id

    # 3. Check Status
    response = client.get("/api/status")
    assert response.status_code == 200
    # Note: It might be 'idle' or 'running' depending on how fast the background task kicked in/finished.
    # We just check the endpoint works.
    assert "status" in response.json()

    # 4. Stop Agent
    response = client.post("/api/stop")
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"

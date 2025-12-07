def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AutoReflex OODA Engine Online", "status": "active"}

def test_optimize_endpoint(client):
    payload = {
        "description": "Create a python script",
        "context_files": [],
        "constraints": "No external libs"
    }
    response = client.post("/api/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "optimized_prompt" in data
    assert "original_task" in data
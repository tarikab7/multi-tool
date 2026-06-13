from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_run_tool_invalid_name():
    response = client.post("/api/run/invalid_tool_name_that_does_not_exist", json={})
    assert response.status_code == 404
    assert "Tool 'invalid_tool_name_that_does_not_exist' not found" in response.json()["detail"]

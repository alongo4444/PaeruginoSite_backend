from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)


def test_check_get_defense_systems_names_true():
    """
    checks the endpoint of the defense systems names
    """
    response = client.get("/api/v1/defense")
    assert response.status_code == 200
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_check_get_iso_types_true():
    """
    checks the endpoint of the isolation type
    """
    response = client.get("/api/v1/isolation")
    assert response.status_code == 200


def test_check_get_attributes_true():
    """
    checks the endpoint of the isolation type
    """
    response = client.get("/api/v1/isolation/attributes")
    assert response.status_code == 200


def test_check_isoTypes_true():
    """
    checks the endpoint of the isolation type
    """
    response = client.get("/api/v1/isolation/")
    assert response.status_code == 200

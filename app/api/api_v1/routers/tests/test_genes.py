from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)


def test_check_get_genes_true():
    """
    check the endpoint of getting genes
    """
    response = client.get("http://127.0.0.1:8800/api/v1/genes")
    assert response.status_code == 200


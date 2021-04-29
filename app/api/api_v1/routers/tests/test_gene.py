from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# requirement 4.1

def test_get_gene_true():
    """
    check get all the genes in the system
    """
    response = client.get("/api/v1/genes")
    assert response.status_code == 200
    assert len(response.json()) == 6021


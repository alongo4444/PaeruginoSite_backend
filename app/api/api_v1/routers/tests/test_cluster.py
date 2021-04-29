from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_gene_strain_id_true():
    """
    check the endpoint of the strain id
    """
    response = client.get("/api/v1/cluster/get_gene_strain_id/GCF_000014625.1")
    assert response.status_code == 200
    assert len(response.json()) == 6021


def test_get_gene_strain_id_false():
    '''
    check if the strain not exist
    '''
    response = client.get("/api/v1/cluster/get_gene_strain_id/GCF_I0d3Ot")
    assert response.status_code == 400
    assert response.content == b'No Results'


# def test_get_defense_system_names_false():
#
#     response = client.get("/api/v1/cluster/get_defense_system_names")
#     assert response.status_code == 200
#     assert response.content == b'No Results'

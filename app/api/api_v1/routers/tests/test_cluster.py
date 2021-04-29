from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# requirement 4.7

def test_get_gene_strain_id_true():
    """
    check if the strain exist and returning all of th strain genes
    """
    response = client.get("/api/v1/cluster/get_gene_strain_id/GCF_000014625.1")
    assert response.status_code == 200
    assert len(response.json()) == 6021


def test_get_gene_strain_id_false():
    """
    check if the strain not exist
    """
    response = client.get("/api/v1/cluster/get_gene_strain_id/GCF_I0d3Ot")
    assert response.status_code == 400
    assert response.content == b'No Results'


data = {'list_strain_gene': ['PA14-PA14_RS00005']}


# def test_Cluster_Tree_true():
#     response = client.get("/api/v1/cluster/cluster_tree?list_strain_gene=PA14-PA14_RS00025&list_strain_gene=PA14-PA14_RS00095")
#     assert response.status_code == 200
#

#db = next(get_db())
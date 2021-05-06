from fastapi.testclient import TestClient
from app.main import app
import itertools
client = TestClient(app)

def_names = ["ABI", "BREX", "DISARM", "CRISPR", "DISARMassociated", "DND", "RM", "TA",
             "WADJET", "ZORYA", "HACHIMAN", "LAMASSU", "SEPTU", "THOERIS", "GABIJA", "DRUANTIA", "KIWA", "PAGOS",
             "SHEDU"]



def test_DownloadGenesTrue():
    """
    check the download endpoint
    """
    response = client.get("/api/v1/genes/download_genes?selectedC=start&selectedC=end&selectedAS=GCF_000014625.1")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=export.csv"


def test_DownloadGenesFalse():
    """
    check the download endpoint when the column doesnt exist
    """
    # col not exist
    response = client.get("/api/v1/genes/download_genes?selectedC=start&selectedC=e&selectedAS=GCF_000014625.1")
    assert response.status_code == 400

    # gene not exist
    response = client.get("/api/v1/genes/download_genes?selectedC=start&selectedC=end&selectedAS=GCF_0000146")
    assert response.status_code == 400


def test_DownloadDefenseSystemsTrue():
    """
    check the download genes endpoint
    """
    for a, b in itertools.combinations(def_names, 2):
        response = client.get("/api/v1/genes/genes_by_defense?selectedC=s"
                              "tart&selectedC=end&selectedAS={}&selectedAS={}".format(a, b))
        assert response.status_code == 200
        assert response.headers["Content-Disposition"] == "attachment; filename=export.csv"


def test_DownloadDefenseSystemsFalse():
    """
    check the download genes endpoint when the column doesnt exist
    """
    # col not exist
    response = client.get("/api/v1/genes/genes_by_defense?selectedC=start&selectedC=e&selectedAS=abi")
    assert response.status_code == 400

    # defense system not exist
    response = client.get("/api/v1/genes/genes_by_defense?selectedC=start&selectedC=end&selectedAS=nonExist")
    assert response.status_code == 400


def test_DownloadGenesByClusterTrue():
    """
    check the download cluster endpoint
    """
    response = client.get("/api/v1/genes/genes_by_cluster?genes=PA14_RS00025&csv=false&prot=true")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=export.txt"


def test_DownloadGenesByClusterFalse():
    """
    check the download cluster endpoint column doesn't exist
    """
    response = client.get("/api/v1/genes/genes_by_cluster?genes=dhfgh&csv=false&prot=true")
    assert response.status_code == 400


def test_GetGenesTrue():
    """
    check the endpoint of getting genes
    """
    response = client.get("http://127.0.0.1:8800/api/v1/genes")
    assert response.status_code == 200


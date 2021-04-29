from fastapi.testclient import TestClient

from app.db.crud import get_genes, get_strains_index, get_strains_names, get_strains_cluster, get_gene_by_strain, \
    get_defense_systems_of_genes, get_genes_by_cluster
from app.db.session import get_db
from app.main import app

client = TestClient(app)
db = next(get_db())


def test_get_genes_crud_true():
    response = get_genes(db)
    assert len(response) == 6021


def test_get_strains_index_true():
    response = get_strains_index(db)
    assert len(response) == 4581


def test_get_strains_names_true():
    response = get_strains_names(db)
    assert len(response) == 4581


cluster_list_test = ['PA14-PA14_RS00475', 'PA14-PA14_RS00195', 'PA14-PA14_RS00105']
cluster_list_test_false = ['PAO1-PA14_RS00475', 'PAO1-PA14_RS00195', 'PAO1-PA14_RS00105']


def test_get_strains_cluster_true():
    list_assert = [(4479, "{'2': 1, '3': 1, '18': 1, '25': 1, '27': 1, '32': 1, '36': 1, '37': 1, '41': 1}"),
                   (26955,
                    "{'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, '13': 1, '14': 1, '15': 1, '16': 1, '17': 1, '18': 1, '19': 1, '20': 1, '21': 1, '22': 1, '23': 1, '24': 1, '25': 1, '26': 1, '27': 1, '28': 1, '29': 1, '30': 1, '31': 1, '32': 1, '33': 1, '34': 1, '35': 2, '36': 1, '37': 1, '38': 1, '39': 1, '40': 1, '41': 1, '42': 1, '43': 1, '44': 1, '45': 1, '46': 1, '47': 1, '48': 1, '49': 1, '50': 1, '51': 1}"),
                   (7318,
                    "{'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, '13': 1, '14': 1, '15': 1, '16': 1, '17': 1, '18': 1, '19': 1, '20': 1, '21': 1, '22': 1, '23': 1, '24': 1, '25': 1, '26': 1, '27': 1, '28': 1, '29': 1, '30': 1, '31': 1, '32': 1, '34': 1, '35': 2, '36': 1, '37': 1, '38': 1, '39': 1, '40': 1, '41': 1, '42': 1, '43': 1, '44': 1, '45': 1, '47': 1, '48': 1, '49': 1, '50': 1, '51': 1}")]

    response = get_strains_cluster(db, cluster_list_test)
    assert len(response) == 3
    assert response == list_assert


def test_get_strains_cluster_false():
    response = get_strains_cluster(db, cluster_list_test_false)
    assert len(response) == 0
    assert response == []


def test_get_gene_by_strain_true():
    response = get_gene_by_strain(db, "GCF_000014625.1")
    assert len(response) == 6021


def test_get_gene_by_strain_false():
    response = get_gene_by_strain(db, "GCF_000006765.1")
    assert len(response) == 0


def test_get_defense_systems_of_genes_true():
    response = get_defense_systems_of_genes(db, "PA14")
    assert len(response) == 121


def test_get_defense_systems_of_genes_false():
    response = get_defense_systems_of_genes(db, "PAO1")
    assert response == "No Results"


def test_get_genes_by_cluster_true():
    response = get_genes_by_cluster(db, ["PA14_RS02190","PA14_RS03770"])
    assert len(response) == 2

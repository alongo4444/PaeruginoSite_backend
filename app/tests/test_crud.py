from fastapi.testclient import TestClient

from app.db.crud import *
from app.db.session import get_db
from app.main import app

client = TestClient(app)
db = next(get_db())


def test_get_genes_crud_true():
    """
    check if the function return all of the genes from the db
    """
    response = get_genes(db)
    assert len(response) <= 6021


def test_get_strains_index_true():
    """
    check if the function return all of the strain and their index's from the db
    """
    response = get_strains_index(db)
    assert len(response) <= 4581
    assert list(response[0].keys()) == ['index', 'name']


def test_get_strains_names_true():
    """
    check if the function return all of the strain name and their key's from the db
    """
    response = get_strains_names(db)
    assert len(response) <= 4581
    assert list(response[0].keys()) == ['name', 'key']


cluster_list_test = ['PA14-PA14_RS00475', 'PA14-PA14_RS00195', 'PA14-PA14_RS00105']
cluster_list_test_false = ['PAO1-PA14_RS00475', 'PAO1-PA14_RS00195', 'PAO1-PA14_RS00105']


def test_get_strains_cluster_true():
    """
     check if the function return all of the clusters and the strains in the clusters from the db
     """
    list_assert = [(4479, "{'2': 1, '3': 1, '18': 1, '25': 1, '27': 1, '32': 1, '36': 1, '37': 1, '41': 1}"),
                   (26955,
                    "{'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, "
                    "'11': 1, '12': 1, '13': 1, '14': 1, '15': 1, '16': 1, '17': 1, '18': 1, '19': 1, '20': 1, "
                    "'21': 1, '22': 1, '23': 1, '24': 1, '25': 1, '26': 1, '27': 1, '28': 1, '29': 1, '30': 1, "
                    "'31': 1, '32': 1, '33': 1, '34': 1, '35': 2, '36': 1, '37': 1, '38': 1, '39': 1, '40': 1, "
                    "'41': 1, '42': 1, '43': 1, '44': 1, '45': 1, '46': 1, '47': 1, '48': 1, '49': 1, '50': 1, "
                    "'51': 1}"),
                   (7318,
                    "{'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, "
                    "'11': 1, '12': 1, '13': 1, '14': 1, '15': 1, '16': 1, '17': 1, '18': 1, '19': 1, '20': 1, "
                    "'21': 1, '22': 1, '23': 1, '24': 1, '25': 1, '26': 1, '27': 1, '28': 1, '29': 1, '30': 1, "
                    "'31': 1, '32': 1, '34': 1, '35': 2, '36': 1, '37': 1, '38': 1, '39': 1, '40': 1, '41': 1, "
                    "'42': 1, '43': 1, '44': 1, '45': 1, '47': 1, '48': 1, '49': 1, '50': 1, '51': 1}")]

    response = get_strains_cluster(db, cluster_list_test)
    assert len(response) == 3
    assert response == list_assert


def test_get_strains_cluster_false():
    """
     check if the function return nothing from the db
    """
    response = get_strains_cluster(db, cluster_list_test_false)
    assert len(response) == 0
    assert response == []


def test_get_strain_isolation_true():
    """
    check if the function return all of the strain and their isolation type from the db
    """
    response = get_strain_isolation(db)
    assert len(response) <= 4581
    assert list(response.columns) == ['strain', 'isolation_type']


def test_get_strain_id_name_true():
    """
     check if the function return all of the strain from the db
    """
    response = get_strain_id_name(db)
    assert len(response) <= 4581
    assert response.columns == ['strain']


def test_get_strain_isolation_mlst_true():
    """
     check if the function return all of the index's, strains, isolation_type,MLST from the db
    """
    response = get_strain_isolation_mlst(db)
    assert len(response) <= 4581
    assert list(response.columns) == ['index', 'strain', 'isolation_type', 'MLST']


def test_get_gene_by_strain_true():
    """
     check if the function return all of the genes according to a certain strain from the db
    """
    response = get_gene_by_strain(db, "GCF_000014625.1")
    assert len(response) <= 6021


def test_get_gene_by_strain_false():
    """
     check if the function return nothing from the db when a non existing gene is inserted as parameter
    """
    response = get_gene_by_strain(db, "GCF_000006765.1")
    assert len(response) == 0


def test_get_defense_systems_of_genes_true():
    """
     check if the function return all of the defense systems according to a certain strain from the db
    """
    response = get_defense_systems_of_genes(db, "PA14")
    assert len(response) <= 121


def test_get_defense_systems_of_genes_false():
    """
     check if the function return nothing from the db when a non existing strain is inserted as parameter
    """
    response = get_defense_systems_of_genes(db, "PAO1")
    assert response == "No Results"


def test_get_genes_by_cluster_true():
    """
     check if the function return dataframe of the cluster according to a certain genes from the db
    """
    response = get_genes_by_cluster(db, ['PA14_RS00095', 'PA14_RS00245', ''])
    assert len(response) == 2
    assert response['cluster_index'].iloc[0] == 17021
    assert response['cluster_index'].iloc[1] == 14292


def test_get_genes_by_cluster_false():
    """
     check if the function return nothing from the db when a non existing genes is inserted as parameter
    """
    response = get_genes_by_cluster(db, ['PA14_RS452343', 'PA14_RS66464', ''])
    assert len(response) == 0


def test_get_defense_systems_of_two_strains_true():
    """
     check if the function return dictionary of the strain that the defense systems
     appears in from the db
    """
    response = get_defense_systems_of_two_strains(db, 'BREX', 'ABI')
    assert len(response) <= 4581
    # assert list(response[0].keys()) == ['index', 'brex', 'abi']


def test_get_defense_systems_names_true():
    """
     check if the function return the defense systems names from the db
    """
    response = get_defense_systems_names(db)
    assert len(response) <= 49


def test_get_all_strains_of_defense_system_true():
    """
     check if the function return a dataframe of all of the strains and their defense system
     the defense systems names from the db
    """
    response = get_all_strains_of_defense_system(db, 'ABI')
    assert len(response) <= 4581
    assert list(response.columns) == ['index', 'abi']


def test_get_strain_column_data_true():
    """
    check if the function return a dataframe of all of the strains and their isolation type from the db
    """
    response = get_strain_column_data(db, 'isolation_type')
    assert len(response) <= 4581
    assert list(response.columns) == ['index', 'isolation_type']


def test_dict_of_clusters_related_to_gene_true():
    """
    check if function returns dataframe that contains the cluster,
    the gene and the dictionary of all the other cluster from the db
    """
    response = dict_of_clusters_related_to_gene(db, 'PA14', 'PA14_RS00005')
    assert len(response) == 1
    assert response['index'].iloc[0] == 3456
    assert list(response.columns) == ['index', 'pa14', 'combined_index']


def test_dict_of_clusters_related_to_gene_false():
    """
    check if the function return nothing from the db when a non existing gene is inserted as parameter
    """
    response = dict_of_clusters_related_to_gene(db, 'PA14', 'PA14_RS454577')
    assert response == "No Results"


def test_get_strains_MLST_true():
    """
    check if the function return dataframe of all the strain id and the strain name with the MLST
    metadata in a dataframe for the browse in the phylogenetic tree from the db
    """
    response = get_strains_MLST(db)
    assert len(response) <= 4581


def test_get_colors_dict_true():
    """
    check if the function returns a dictionary of colors from the db
    """
    response = get_colors_dict(db)
    assert len(response) == 49

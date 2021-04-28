from fastapi.testclient import TestClient
import app.api.api_v1.routers.strains as strains
from app.main import app
client = TestClient(app)

# Integration Tests - Strains


def test_get_colors_true():
    """
    check if we get the colors of the defense system
    """
    response = client.get("api/v1/strains/defSystemsColors")
    assert response.status_code == 200


def test_get_strain_genes_def_systems_true():
    """
    check if we receive the genes that contains defense system
    """
    response = client.get("api/v1/strains/strainGenesDefSystems/PA14")
    assert response.status_code == 200


def test_get_strain_genes_def_systems_false():
    """
    check if we receive the 400 response because the strain doesn't exist
    """
    response = client.get("api/v1/strains/strainGenesDefSystems/PA145")
    assert response.status_code == 400
    assert response.content == b'No Results'


def test_get_strains_indexes():
    """
    check the strain indexes endpoint
    """
    response = client.get("api/v1/strains/indexes")
    assert response.status_code == 200


def test_get_strains_list():
    """
    check the strains list endpoint
    """
    response = client.get("api/v1/strains/")
    assert response.status_code == 200


def test_load_def_systems_names():
    """
    check that the loading works properly
    """
    names = strains.load_def_systems_names()
    assert len(names) > 0


def test_load_colors_def_systems():
    """
    check that the color loading works properly
    """
    colors = strains.load_colors()
    assert len(colors) > 0


# UNIT TESTING

def test_check_resolution_zero():
    """
    check the resolution internal function
    """
    assert strains.get_resolution(0) == 300


def test_check_resolution_positive():
    """
    check the resolution internal function
    """
    res = strains.get_resolution(300)
    assert res == 0.183 * 300 + 23.672


def check_offset_zero():
    """
    check the internal offset function
    """
    assert strains.get_offset(0) is "0.03"


def check_offset_positive():
    """
    check the internal offset function
    """
    assert strains.get_offset(300) is str(-0.0001 * 300 + 0.15)

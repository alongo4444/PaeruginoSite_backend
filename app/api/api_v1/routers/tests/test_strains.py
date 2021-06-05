from fastapi.testclient import TestClient
import app.api.api_v1.routers.strains as strains
from app.main import app
client = TestClient(app)

# Integration Tests - Strains


def test_getColorsTrue():
    """
    check if we get the colors of the defense system
    """
    response = client.get("api/v1/strains/defSystemsColors")
    assert response.status_code == 200


def test_getGenesDefSystemsTrue():
    """
    check if we receive the genes that contains defense system
    """
    response = client.get("api/v1/strains/strainGenesDefSystems/GCF_000404265.1")
    assert response.status_code == 200


def test_getGenesDefSystemsFalse():
    """
    check if we receive the 200 response because the strain doesn't exist (we send back default)
    """
    response = client.get("api/v1/strains/strainGenesDefSystems/PA145")
    assert response.status_code == 200


def test_getStrainIndexesTrue():
    """
    check the strain indexes endpoint
    """
    response = client.get("api/v1/strains/indexes")
    assert response.status_code == 200


def test_getStrainNamesTrue():
    """
    check the strains list endpoint
    """
    response = client.get("api/v1/strains/")
    assert response.status_code == 200


def test_loadDefSystemNames():
    """
    check that the loading works properly
    """
    names = strains.load_def_systems_names()
    assert len(names) > 0


def test_loadColorsDefSystemNames():
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
    assert strains.get_resolution(0, 1) == 360.5


def test_check_resolution_positive():
    """
    check the resolution internal function
    """
    res = strains.get_resolution(300, 2)
    assert res == 0.183 * 300 + 23.672



def test_check_offset_zero():
    """
    check the internal offset function
    """
    assert strains.get_offset(0) in "0.03"


def test_check_offset_positive():
    """
    check the internal offset function
    """
    assert strains.get_offset(300) in str(-0.0001 * 300 + 0.15)


def test_check_spacing_zero():
    """
    check the spacing internal function
    """
    assert strains.get_offset(0) in str(0.03)


def test_check_spacing_positive():
    """
    check the spacing internal function
    """
    assert strains.get_offset(300) in str(-0.0001 * 300 + 0.15)


def test_check_font_size_zero():
    """
    check the font size internal function
    """
    assert strains.get_font_size(0) in '100'


def test_check_font_size_positive():
    """
    check the font size internal function
    """
    assert strains.get_font_size(300) in str(0.06 * 300 + 15.958)


def test_check_first_layer_offset_zero():
    """
    check the first layer offset internal function
    """
    assert strains.get_first_layer_offset(0) in str(0.08)


def test_check_first_layer_offset_bigger():
    """
    check the first layer offset internal function
    """
    assert strains.get_first_layer_offset(1101) in str(0.08)


def test_check_first_layer_offset_positive():
    """
    check the first layer offset internal function
    """
    assert strains.get_first_layer_offset(300) in str(0.00000038 * (300 ** 2) - 0.00097175 * 300 + 0.67964847)

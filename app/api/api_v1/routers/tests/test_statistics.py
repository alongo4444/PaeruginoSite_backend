from fastapi.testclient import TestClient
from app.main import app
import itertools
client = TestClient(app)

# requirements 4.5

def_names = ["ABI", "BREX", "DISARM", "CRISPR", "DISARMassociated", "DND", "RM", "TA",
"WADJET", "ZORYA", "HACHIMAN", "LAMASSU", "SEPTU", "THOERIS", "GABIJA", "DRUANTIA", "KIWA", "PAGOS", "SHEDU"]

# CORRELATION BETWEEN TWO DEFENSE SYSTEMS

def test_correlation_between_two_def_systems_true():
    """
    check if the response is positive with every combination of defense systems
    """
    for a, b in itertools.combinations(def_names, 2):
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems="+
                              a+"&systems="+b)
            assert response.status_code == 200


def test_correlation_between_same_defense_system_false():
    """
    check how the system handles the correlation between the same defense system
    """
    for item in def_names:
        response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems="+
                            item+"&systems="+item)
        assert response.status_code == 400
        assert response.content == b'Same Defense System'


def test_correlation_between_real_defense_system_and_unreal_false():
    """
    check how the system handles the correlation between one existing defense system
    and one that doesn't exist
    """
    for item in def_names:
        response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems="+
                            item+"&systems="+"test")
        assert response.status_code == 400
        assert response.content == b"Defense system doesn't exist"


def test_correlation_between_two_unreal_defense_system_false():
    """
    check how the system handles the correlation between twp defense system that doesn't exist
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems=test&systems=test1")
    assert response.status_code == 400
    assert response.content == b"Defense system doesn't exist"


def test_correlation_between_defense_systems_missing_one_value_false():
    """
    check how the system handles one missing value in the query params
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems=")
    assert response.status_code == 400
    assert response.content == b"Wrong number of parameters"


def test_correlation_between_defense_systems_empty_values_false():
    """
    check how the system handles two missing values in the query params
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?")
    assert response.status_code == 400
    assert response.content == b"Wrong number of parameters"


# CORRELATION BETWEEN ATTRIBUTE AND DEFENSE SYSTEM

attr_list = ['size', 'gc', 'cds']


def test_correlation_between_defense_system_and_attribute_true():
    """
    checks how the system handles each combination of defense system and attribute
    """
    for sys in def_names:
        for attr in attr_list:
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?system="+sys+"&category="+attr)
            assert response.status_code == 200


def test_correlation_between_unreal_def_sys_real_attribute_false():
    """
    checks how the system handles a defense system that doesn't exist and an
    attribute that does exist
    """
    for attr in attr_list:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?system=" + "test"+ "&category=" + attr)
        assert response.status_code == 400
        assert response.content == b"Defense system doesn't exist"


def test_correlation_between_real_def_sys_unreal_attribute_false():
    """
    checks how the system handles a defense system that does exist and an
    attribute that doesn't exist
    """
    for sys in def_names:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?system=" + sys + "&category=test")
        assert response.status_code == 400
        assert response.content == b"Wrong category name"


def test_correlation_between_missing_def_sys_and_attribute_false():
    """
    checks how the system handles a missing defense system that does exist and an attribute
    """
    for attr in attr_list:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?&category="+attr)
        assert response.status_code == 422


def test_correlation_between_missing_attribute_real_def_false():
    """
    checks how the system handles a missing attribute and a defense system that does exist
    """
    for sys in def_names:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?&system="+sys)
        assert response.status_code == 422

# CORRELATION BETWEEN ISOLATION TYPE AND DEFENSE SYSTEM


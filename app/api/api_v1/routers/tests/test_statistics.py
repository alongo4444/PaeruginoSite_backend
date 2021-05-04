from fastapi.testclient import TestClient

from app.api.api_v1.routers.statistics import renameDefColumn
from app.main import app
import itertools
client = TestClient(app)

# requirements 4.5

def_names = ["ABI", "BREX", "DISARM", "CRISPR", "DND", "RM", "TA",
"WADJET", "ZORYA", "HACHIMAN", "LAMASSU", "SEPTU", "THOERIS", "GABIJA", "DRUANTIA", "KIWA", "PAGOS", "SHEDU"]

# CORRELATION BETWEEN TWO DEFENSE SYSTEMS


def test_CorrelationTwoDefSystemsTrue():
    """
    check if the response is positive with every combination of defense systems
    """
    for a, b in itertools.combinations(def_names, 2):
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems="+
                              a+"&systems="+b)
            assert response.status_code == 200


def test_CorrelationSameDefSystemsFalse():
    """
    check how the system handles the correlation between the same defense system
    """
    for item in def_names:
        response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems="+
                            item+"&systems="+item)
        assert response.status_code == 400
        assert response.content == b'Same Defense System'


def test_CorrelationOneDefSystemCorruptFalse():
    """
    check how the system handles the correlation between one existing defense system
    and one that doesn't exist
    """
    for item in def_names:
        response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems="+
                            item+"&systems="+"test")
        assert response.status_code == 400
        assert response.content == b"Defense system doesn't exist"


def test_CorrelationTwoDefSystemCorruptFalse():
    """
    check how the system handles the correlation between two defense system that doesn't exist
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems=test&systems=test1")
    assert response.status_code == 400
    assert response.content == b"Defense system doesn't exist"


def test_CorrelationTwoDefSystemMissValueFalse():
    """
    check how the system handles one missing value in the query params
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?systems=")
    assert response.status_code == 400
    assert response.content == b"Wrong number of parameters"


def test_CorrelationTwoDefSystemEmptyValueFalse():
    """
    check how the system handles two missing values in the query params
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystems?")
    assert response.status_code == 400
    assert response.content == b"Wrong number of parameters"


# CORRELATION BETWEEN ATTRIBUTE AND DEFENSE SYSTEM

attr_list = ['size', 'gc', 'cds']


def test_CorrelationDefSystemAttrTrue():
    """
    checks how the system handles each combination of defense system and attribute
    """
    for sys in def_names:
        for attr in attr_list:
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?system="+sys+"&category="+attr)
            assert response.status_code == 200


def test_CorrelationCorruptDefSystemAttrFalse():
    """
    checks how the system handles a defense system that doesn't exist and an
    attribute that does exist
    """
    for attr in attr_list:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?system=" + "test"+ "&category=" + attr)
        assert response.status_code == 400
        assert response.content == b"Defense system doesn't exist"


def test_CorrelationDefSystemCorruptAttrFalse():
    """
    checks how the system handles a defense system that does exist and an
    attribute that doesn't exist
    """
    for sys in def_names:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?system=" + sys + "&category=test")
        assert response.status_code == 400
        assert response.content == b"Wrong category name"


def test_CorrelationMissingDefSystemAttrFalse():
    """
    checks how the system handles a missing defense system that does exist and an attribute
    """
    for attr in attr_list:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?&category="+attr)
        assert response.status_code == 422


def test_CorrelationDefSystemMissingAttrFalse():
    """
    checks how the system handles a missing attribute and a defense system that does exist
    """
    for sys in def_names:
        response = client.get(
            "api/v1/statistics/correlationBetweenDefenseSystemAndAttribute?&system="+sys)
        assert response.status_code == 422

# CORRELATION BETWEEN ISOLATION TYPE AND DEFENSE SYSTEM


iso_type = ['Environmental/other', 'Clinical']


def test_CorrelationDefSystemIsotypeTrue():
    """
    checks how the system handles each combination of defense system and isolation type
    """
    for sys in def_names:
        for iso in iso_type:
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndIsolationType?system="+sys+"&isoType="+iso)
            assert response.status_code == 200


def test_CorrelationCorruptDefSystemIsotypeFalse():
    """
    checks how the system handles unreal defense system and real isolation type
    """
    for iso in iso_type:
        response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndIsolationType?system=test"+"&isoType="+iso)
        assert response.status_code == 400
        assert response.content == b"Defense system doesn't exist"


def test_CorrelationDefSystemCorruptIsotypeFalse():
    """
    checks how the system handles unreal isolation type and real defense system
    """
    for sys in def_names:
        response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndIsolationType?system="
                              +sys+"&isoType=test")
        assert response.status_code == 400
        assert response.content == b"Wrong isotype"


def test_CorrelationDefSystemMissIsotypeFalse():
    """
    checks how the system handles missing isolation type and real defense system
    """
    for sys in def_names:
        response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndIsolationType?system="+sys)
        assert response.status_code == 422


def test_CorrelationMissDefSystemIsotypeFalse():
    """
    checks how the system handles missing isolation type and real defense system
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndIsolationType?isoType=clinical")
    assert response.status_code == 422


# CORRELATION BETWEEN CLUSTER AND DEFENSE SYSTEM


def test_CorrelationDefSystemClusterTrue():
    """
    checks how the system handles each combination of defense system and pa14 and specific gene
    """
    for sys in def_names:
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndCluster?system="+sys+
                                  "&strain=PA14&gene=RS13565")
            assert response.status_code == 200


def test_CorrelationDefSystemClusterCorruptGeneFalse():
    """
    checks how the system handles a wrong gene name
    """
    for sys in def_names:
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndCluster?system="+sys+
                                  "&strain=PA14&gene=RS135656")
            assert response.status_code == 400
            assert response.content == b"Gene doesn't exist"


def test_CorrelationDefSystemClusterCorruptStrainFalse():
    """
    checks how the system handles wrong strain name
    """
    for sys in def_names:
            response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndCluster?system="+sys+
                                  "&strain=PA145&gene=RS13565")
            assert response.status_code == 400
            assert response.content == b"Strain doesn't exist"


def test_CorrelationDefSystemClusterCorruptDefFalse():
    """
    checks how the system handles wrong defense system name
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndCluster?system=test"
                                  "&strain=PA14&gene=RS13565")
    assert response.status_code == 400
    assert response.content == b"Defense system doesn't exist"


def test_CorrelationDefSystemClusterMissStrainFalse():
    """
    checks how the system handles missing strain
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndCluster?system=BREX&gene=RS13565")
    assert response.status_code == 422


def test_CorrelationDefSystemClusterMissGeneFalse():
    """
    checks how the system handles missing gene
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndCluster?system=BREX&strain=PA14")
    assert response.status_code == 422


def test_CorrelationDefSystemClusterMissDefFalse():
    """
    checks how the system handles missing defense system name
    """
    response = client.get("api/v1/statistics/correlationBetweenDefenseSystemAndCluster?&strain=PA14&gene=RS13565")
    assert response.status_code == 422


# CORRELATION BETWEEN CLUSTER AND ISOLATION TYPE


def test_CorrelationIsotypeClusterTrue():
    """
    checks how the system handles each combination of isotype and certain gene and strain
    """
    for iso in iso_type:
            response = client.get("api/v1/statistics/correlationBetweenClusterAndIsolationType?"
                                  "isoType="+iso+"&strain=PA14&gene=RS13565")
            assert response.status_code == 200


def test_CorrelationIsotypeClusterCorruptGeneFalse():
    """
    checks how the system handles a wrong gene name
    """
    for iso in iso_type:
            response = client.get("api/v1/statistics/correlationBetweenClusterAndIsolationType?isoType="+iso+
                                  "&strain=PA14&gene=RS135656")
            assert response.status_code == 400
            assert response.content == b"Gene doesn't exist"


def test_CorrelationIsotypeClusterCorruptStrainFalse():
    """
    checks how the system handles a wrong strain name
    """
    for iso in iso_type:
            response = client.get("api/v1/statistics/correlationBetweenClusterAndIsolationType?isoType="+iso+
                                  "&strain=PA145&gene=RS13565")
            assert response.status_code == 400
            assert response.content == b"Strain doesn't exist"


def test_CorrelationIsotypeClusterCorruptIsotypeFalse():
    """
    checks how the system handles a wrong isotype name
    """
    response = client.get("api/v1/statistics/correlationBetweenClusterAndIsolationType?isoType=test&strain=PA14&gene=RS13565")
    assert response.status_code == 400
    assert response.content == b"Wrong isotype"


def test_CorrelationIsotypeClusterMissIsotypeFalse():
    """
    checks how the system handles missing isotype
    """
    response = client.get("api/v1/statistics/correlationBetweenClusterAndIsolationType?&strain=PA14&gene=RS13565")
    assert response.status_code == 422


def test_CorrelationIsotypeClusterMissStrainFalse():
    """
    checks how the system handles missing strain
    """
    response = client.get("api/v1/statistics/correlationBetweenClusterAndIsolationType?isoType=clinical&gene=RS13565")
    assert response.status_code == 422


def test_CorrelationIsotypeClusterMissGeneFalse():
    """
    checks how the system handles missing gene
    """
    response = client.get("api/v1/statistics/correlationBetweenClusterAndIsolationType?isoType=clinical&strain=PA14")
    assert response.status_code == 422


def test_ConvertDefSystemName():
    """
    checks the internal string function
    """
    test1 = renameDefColumn("RM")
    assert test1 in "rm"
    test2 = renameDefColumn("TA|TypeII")
    assert test2 in "ta_typeii"

'''
def test_convert_defense_system_name_2():
    """
    checks the internal string function
    """
    test2 = renameDefColumn("TA|TypeII")
    assert test2 in "ta_typeii"
'''
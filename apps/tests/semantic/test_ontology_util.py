from assertpy import assert_that

from semantic.ontology_loader import load_from_path
from semantic.ontology_util import *


class EntityMock:
    def __init__(self, name):
        self.name = name


onto = load_from_path("./tests/test_data/test-ontology.rdf")


class TestEntityNameTransformation:

    def test_native_name_of_entity_1(self):
        assert natural_name_of_entity(EntityMock("One")) == "One"

    def test_native_name_of_entity_2(self):
        assert natural_name_of_entity(EntityMock("OneTwo")) == "One Two"

    def test_entity_of_natural_name(self):
        ontology_util = OntologyUtil(onto)
        found_entity = ontology_util.entity_of_natural_name("Integer Multiplication")
        assert onto.IntegerMultiplication == found_entity


class TestEntityTraversals:

    def test_is_leaf_entity(self):
        assert is_leaf_entity(onto.IntegerMultiplication)
        assert not is_leaf_entity(onto.Mathematics)
        assert not is_leaf_entity(onto.IntegerArithmetic)

    def test_is_root_entity(self):
        assert is_root_entity(onto.Mathematics)
        assert not is_root_entity(onto.IntegerMultiplication)
        assert not is_root_entity(onto.IntegerArithmetic)

    def test_list_root_entities(self):
        ontology_util = OntologyUtil(onto)
        result = ontology_util.list_root_entities(onto.Ability)
        assert len(result) == 7
        assert_that(result).contains(onto.AnalyticalCapability)

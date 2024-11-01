from api.ontology_serializer import serialize_entity_tree
from semantic.ontology_loader import load_from_path

onto = load_from_path("./tests/test_data/test-ontology.rdf")

class TestTreeSerialization:

    def test_serialize_entity_tree(self):
        result = serialize_entity_tree([ onto.AbstractionScope ], "hasPartScope")
        assert isinstance(result, list)

    def test_serialize_entity_tree_without_children(self):
        result = serialize_entity_tree([ onto.Arithmetic ], "expandsArea")
        assert isinstance(result, list)

    def test_serialize_entity_tree_2(self):
        result = serialize_entity_tree([ onto.IntegerMultiplication ], "expandsArea")
        assert isinstance(result, list)

    def test_serialize_entity_tree_3(self):
        result = serialize_entity_tree([ onto.IntegerArithmetic ], "expandsArea")
        print(result)
        assert isinstance(result, list)
from api.ontology_serializer import serialize_entity_tree, serialize_entity_tree_with_parent_relations
from semantic.ontology_loader import load_from_path

onto = load_from_path("./tests/test_data/test-ontology.rdf")

class TestTreeSerialization:

    def test_serialize_entity_tree(self):
        result = serialize_entity_tree([ onto.AbstractionScope ], "hasPartScope")
        assert isinstance(result, list)

    def test_serialize_entity_tree_without_children(self):
        result = serialize_entity_tree([ onto.Arithmetic ], "expandsArea")
        assert isinstance(result, list)

    def test_serialize_entity_tree_with_parent_relations(self):
        result = serialize_entity_tree_with_parent_relations([ onto.IntegerMultiplication ], "expandsArea", "partOfArea")
        print(result)
        assert isinstance(result, list)

    def test_serialize_entity_tree_with_parent_relations_2(self):
        result = serialize_entity_tree_with_parent_relations([ onto.IntegerArithmetic ], "expandsArea", "partOfArea")
        print(result)
        assert isinstance(result, list)

    def test_serialize_entity_tree_with_parent_relations_3(self):
        result = serialize_entity_tree_with_parent_relations([ onto.Arithmetic ], "expandsArea", "partOfArea")
        print(result)
        assert isinstance(result, list)
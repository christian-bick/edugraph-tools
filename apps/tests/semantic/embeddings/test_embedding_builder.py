import pytest
from dotenv import load_dotenv

from semantic.embeddings.strategies.embedding_strategy_gemini_v1 import GeminiEmbeddingStrategy
from semantic.ontology_loader import load_from_path
from semantic.ontology_util import OntologyUtil
from tests.entity_mock import EntityMock
from semantic.embeddings.embedding_builder import embed_taxonomy, generate_embedding_input

onto = load_from_path("./tests/test_data/test-ontology.rdf")
onto_util = OntologyUtil(onto)

load_dotenv()

class TestEmbeddingBuilder:

    @pytest.fixture
    def entities(self):
        return [EntityMock('e1', [
            EntityMock('e1-e1', [
                EntityMock('e1-e1-e1'),
                EntityMock('e1-e1-e2')
            ]), EntityMock(
                'e1-e2'
            )]
        )]

    def test_generate_embedding_input(self):
        entities_x = onto_util.list_root_entities(onto.Scope)
        input_map = generate_embedding_input(entities_x)
        print(input_map)

    def test_embed_taxonomy(self):
        entities_x = onto_util.list_root_entities(onto.Scope)
        embedding_map = embed_taxonomy(entities_x, GeminiEmbeddingStrategy())
        for [key, value] in embedding_map.items():
            print(key)
            print(value)
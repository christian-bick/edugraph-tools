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

    def test_generate_embedding_input(self, entities):
        input_map = generate_embedding_input(entities)
        assert input_map == {
            'e1': 'e1-def',
            'e1-e1': 'e1-e1-def',
            'e1-e2': 'e1-e2-def',
            'e1-e1-e1': 'e1-e1-e1-def',
            'e1-e1-e2': 'e1-e1-e2-def'
        }

    def test_embed_taxonomy(self, entities):
        embedding_map = embed_taxonomy(entities, GeminiEmbeddingStrategy())
        assert type(embedding_map['e1']) is list
        assert type(embedding_map['e1-e1']) is list
        assert type(embedding_map['e1-e2']) is list
        assert type(embedding_map['e1-e1-e1']) is list
        assert type(embedding_map['e1-e1-e2']) is list
import pytest

from tests.entity_mock import EntityMock
from semantic.embeddings.embedding_builder import embed_taxonomy

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

    def test_embed_taxonomy(self, entities):
        embed_taxonomy('test', entities)
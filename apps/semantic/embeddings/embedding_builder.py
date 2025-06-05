from semantic.embeddings.embedding_strategy import EmbeddingStrategy
from semantic.ontology_util import *

def embed_taxonomy(entities, strategy: EmbeddingStrategy):
    __embed_entities(entities, strategy)

def __embed_entities(entities, strategy: EmbeddingStrategy):
    for entity in entities:
        strategy.embed_entity(entity)

    for entity in entities:
        if not is_leaf_entity(entity):
            strategy.embed_entity(entity)
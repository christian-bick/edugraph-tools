import json
from typing import Dict

from semantic.embeddings.embedding_strategy import EmbeddingStrategy
from semantic.ontology_util import *


def embed_taxonomy(entities, strategy: EmbeddingStrategy) -> Dict:
    input_map = generate_embedding_input(entities)
    return strategy.embed_entries(input_map)

def generate_embedding_input(entities) -> Dict:
    embedding_map = {}

    for entity in entities:
        embedded_content = natural_name_of_entity(entity)
        if len(definition_of_entity(entity)) > 0:
            embedded_content = definition_of_entity(entity)
        embedding_map[entity.name] = embedded_content


    for entity in entities:
        if not is_leaf_entity(entity):
            embedding_map.update(generate_embedding_input(parts_of_entity(entity)))

    return embedding_map

def __write_dict_to_ldjson(data_dict, filename):
    try:
        with open(filename, 'w') as f:
            for key, value in data_dict.items():
                line_data = {"name": key, "embedding": value}
                f.write(json.dumps(line_data) + '\n')
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")
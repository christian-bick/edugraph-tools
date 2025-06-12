from typing import Tuple, List

import vertexai  # Only for type hinting if GenerativeModel is not directly imported
from dotenv import load_dotenv

from semantic.embeddings.embedder_google import GoogleMultiModalEmbedder, generate_jsonl_from_embeddings, \
    upload_blobs_as_new_files

from semantic.ontology_loader import load_from_path
from semantic.ontology_util import natural_name_of_entity, definition_of_entity, parts_of_entity, is_leaf_entity, \
    OntologyUtil, natural_name_of_entity_name


def generate_embedding_input(entities) -> List[Tuple[str, str]]:
    embedding_input = []

    for entity in entities:
        if not is_leaf_entity(entity):
            leaf_input = generate_embedding_input(parts_of_entity(entity))
            embedding_input.extend(leaf_input)
        else:
            embedded_content = natural_name_of_entity(entity)
            if len(definition_of_entity(entity)) > 0:
                embedded_content = definition_of_entity(entity)
            embedding_input.append((entity.name, embedded_content))

    return embedding_input


class GoogleMultiModalTaxonomyEmbedder:
    def __init__(self, project: str, location: str, bucket_name: str, bucket_path: str,
                 embedder: GoogleMultiModalEmbedder):
        self.project = project
        self.location = location
        self.bucket_name = bucket_name
        self.bucket_path = bucket_path
        self.embedder = embedder

        vertexai.init(project=self.project, location=self.location)

    def embed_taxonomy(self, taxonomy_name: str, name_template: str, definition_template: str, taxonomy_entities: List[Tuple[str, str]]):

        bucket_path_embedded = "examples/embedded-taxonomy"
        embedding_results = []

        for entity in taxonomy_entities:
            name = entity[0]
            definition = entity[1]

            intro = name_template.format(natural_name_of_entity_name(name))

            if definition is None or "":
                description = ""
            else:
                description = definition_template.format(definition.lower())

            embedded_text = f"{intro} {description}"

            print(f"Processing entity: {entity[0]}")
            print(f"Embedded text: {embedded_text}")

            try:
                embedding_result = self.embedder.embed_text(embedded_text)
                embedding_results.append((name, embedding_result))

            except Exception as e:
                print(f"Error processing entity {name}: {e}")

        restricts = [
            {
                "namespace": "dimension",
                "allow": [taxonomy_name]
            }
        ]

        embeddings_json = generate_jsonl_from_embeddings(
            embeddings_data=embedding_results,
            content_type=["taxonomy"],
            content_locale=["en", "en-US"],
            restricts=restricts
        )

        json_filename = f"{taxonomy_name}.json"
        upload_blobs_as_new_files(
            bucket_name=self.bucket_name,
            bucket_path=bucket_path_embedded,
            files_data=[(json_filename, embeddings_json.encode('utf-8'))]
        )


if __name__ == "__main__":
    load_dotenv()
    onto_path = "https://github.com/christian-bick/edugraph-ontology/releases/download/0.1.2/core-ontology.rdf"

    print("Loading ontology")
    ontology = load_from_path(onto_path)
    onto_util = OntologyUtil(ontology)

    print("Initializing Embedder")
    embedder = GoogleMultiModalTaxonomyEmbedder(
        project="edugraph-438718",
        location="europe-west3",
        bucket_name="edugraph-embed",
        bucket_path="examples",
        embedder=GoogleMultiModalEmbedder(model_name="multimodalembedding@001"),
    )

    taxonomies = {
        "Area": [
            "Learning material that focuses on the study of {}.",
            "More precisely the study of {}"
        ],
        #"Ability": "Learning material that primarily involves the ability of {}. {}",
        #"Scope": "Learning material that clearly involves {}. {}"
    }

    for taxonomy_name, entity_template in taxonomies.items():
        print(f"Embedding taxonomy for {taxonomy_name}")

        root_entities = onto_util.list_root_entities(getattr(ontology, taxonomy_name))
        input_entities = generate_embedding_input(root_entities)
        embedder.embed_taxonomy(
            taxonomy_name=taxonomy_name,
            taxonomy_entities=input_entities,
            name_template=entity_template[0],
            definition_template=entity_template[1]
        )

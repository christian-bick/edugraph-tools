
from google.cloud import storage
from dotenv import load_dotenv
import json
import io # Used for simulating file-like object from string

import numpy as np

from pydantic import BaseModel

from google import genai
from google.genai import types

from semantic.embeddings.strategies.embedding_strategy_gemini_v1 import GeminiEmbeddingStrategy
from semantic.ontology_util import OntologyUtil


def load_ndjson_from_gcs(bucket_name: str, blob_name: str) -> list[dict]:
    """
    Loads line-delimited JSON (NDJSON) objects from a Google Cloud Storage blob.

    Args:
        bucket_name (str): The name of your GCS bucket.
        blob_name (str): The full path/name of the file (blob) in the bucket
                         (e.g., 'data/my_ndjson_file.jsonl').

    Returns:
        list[dict]: A list of Python dictionaries, where each dictionary
                    represents a parsed JSON object from a line in the file.
                    Returns an empty list if the file is empty or cannot be read,
                    or if no valid JSON objects are found.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    json_objects = []
    try:
        # Download the blob content as a string
        # download_as_text() is convenient as it handles decoding to utf-8 by default.
        ndjson_content = blob.download_as_text()

        # Use io.StringIO to treat the string content as a file-like object,
        # allowing us to read it line by line efficiently.
        content_stream = io.StringIO(ndjson_content)

        for line_num, line in enumerate(content_stream, 1):
            line = line.strip() # Remove leading/trailing whitespace, including newline characters
            if not line: # Skip empty lines
                continue
            try:
                json_obj = json.loads(line)
                json_objects.append(json_obj)
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse JSON on line {line_num} in '{blob_name}': {e}")
                print(f"  Problematic line: '{line}'")
            except Exception as e:
                print(f"An unexpected error occurred processing line {line_num} in '{blob_name}': {e}")
                print(f"  Problematic line: '{line}'")

        print(f"Successfully loaded {len(json_objects)} JSON objects from '{blob_name}'.")
        return json_objects

    except storage.exceptions.NotFound:
        print(f"Error: Blob '{blob_name}' not found in bucket '{bucket_name}'.")
        return []
    except Exception as e:
        print(f"An error occurred while loading from GCS: {e}")
        return []

def load_taxonomy_embeddings(name):
    bucket_name = "edugraph-embeddings"
    blob_name = "classification/zeroshot/embeddings-{}.json".format(name)
    embedding_objects = load_ndjson_from_gcs(bucket_name, blob_name)
    embedding_tuples = map(lambda embedding: (embedding["name"], embedding["embedding"]), embedding_objects)
    embedding_map = dict(embedding_tuples)
    return embedding_map

def cosine_similarity(embedding1, embedding2):
    """
    Calculates the cosine similarity between two embeddings.

    Args:
        embedding1 (np.array): The first embedding vector.
        embedding2 (np.array): The second embedding vector.

    Returns:
        float: The cosine similarity between the two embeddings.
               Ranges from -1 (completely dissimilar) to 1 (completely similar).
    """
    dot_product = np.dot(embedding1, embedding2)
    norm_embedding1 = np.linalg.norm(embedding1)
    norm_embedding2 = np.linalg.norm(embedding2)

    if norm_embedding1 == 0 or norm_embedding2 == 0:
        return 0.0  # Handle cases where one or both embeddings are zero vectors

    return dot_product / (norm_embedding1 * norm_embedding2)

def cosine_distance(embedding1, embedding2):
    """
    Calculates a "cosine distance" from cosine similarity.
    This is often defined as 1 - cosine_similarity.

    Args:
        embedding1 (np.array): The first embedding vector.
        embedding2 (np.array): The second embedding vector.

    Returns:
        float: The cosine distance between the two embeddings.
               Ranges from 0 (completely similar) to 2 (completely dissimilar).
    """
    return 1 - cosine_similarity(embedding1, embedding2)


def find_closest_embeddings(target_embedding, candidate_embeddings_dict):
    results = []
    for key, candidate_embedding in candidate_embeddings_dict.items():
        distance = cosine_distance(target_embedding, candidate_embedding)
        # Store the distance and the key (name)
        results.append((distance, key))  # Store distance first for easy sorting

    # Sort the results by distance (the first element of the tuple)
    # The default sort order is ascending, which means smallest distance first.
    results.sort(key=lambda x: x[0])

    return results


prompt = """
Describe the provided learning material using the following aspects:

area_description: Describe the area of learning which is covered by the learning material in 2-3 sentences
ability_description: Identify up to 5 cognitive abilities challenged by the learning material and describe each in 2-3 sentences
scope_description: Identify up to 10 pedagogic characteristics about the learning material you haven't mentioned yet and describe each in 2-3 sentences

Make sure to not repeat yourself in your answers.
"""

class PromptResponse(BaseModel):
    area: str
    abilities: list[str]
    scopes: list[str]

class ClassifierEmbeddingsGemini:

    def __init__(self, onto):
        self.onto = onto
        self.onto_util = OntologyUtil(onto)

        self.model = 'gemini-2.0-flash'
        self.client = genai.Client()

        self.embedding_strategy = GeminiEmbeddingStrategy(self.client)


        self.embedding_map_area = load_taxonomy_embeddings("Area")
        self.embedding_map_ability = load_taxonomy_embeddings("Ability")
        self.embedding_map_scope = load_taxonomy_embeddings("Scope")


    def describe_content(self, gemini_file):

        result = self.client.models.generate_content(
            model=self.model,
            contents=[gemini_file, prompt],
            config=types.GenerateContentConfig(
                candidate_count=1,
                temperature=0,
                response_mime_type="application/json",
                response_schema=PromptResponse,
            )
        )
        result_obj = json.loads(result.text)
        return result_obj

    def find_best_matches (self, targets, candidates):

        embedding_targets = self.embedding_strategy.embed_entries(dict(enumerate(targets)))

        best_matches = []
        for embedding_target in embedding_targets.values():
            best_match = find_closest_embeddings(embedding_target, candidates)[0][1]
            best_matches.append(best_match)

        return best_matches

    def find_best_match (self, target, candidates):
        target = self.embedding_strategy.embed_entry(target)
        return find_closest_embeddings(target, candidates)[0][1]

    def classify_content(self, gemini_file):
        descriptions = self.describe_content(gemini_file)

        closest_area = self.find_best_match(descriptions["area"], self.embedding_map_area)
        closest_abilities = self.find_best_matches(descriptions["abilities"], self.embedding_map_ability)
        closest_scopes = self.find_best_matches(descriptions["scopes"], self.embedding_map_scope)

        print(closest_area)
        print(closest_abilities)
        print(closest_scopes)

        classification = {
            "Area": [ closest_area ],
            "Ability": closest_abilities,
            "Scope": closest_scopes
        }
        return classification



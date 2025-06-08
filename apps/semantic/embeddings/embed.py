import json
import os

from dotenv import load_dotenv
from google.cloud import storage

from semantic.embeddings.embedding_builder import embed_taxonomy
from semantic.embeddings.strategies.embedding_strategy_gemini_v1 import GeminiEmbeddingStrategy
from semantic.ontology_loader import load_from_path
from semantic.ontology_util import OntologyUtil

def generate_taxonomy_embeddings(name, onto):
    onto_util = OntologyUtil(onto)
    root_entities = onto_util.list_root_entities(getattr(onto, name))
    embedding_map = embed_taxonomy(root_entities, GeminiEmbeddingStrategy())

    local_filename = './temp/embeddings-{}.json'.format(name)
    write_dict_to_ldjson(embedding_map, local_filename)

    upload_file_to_gcs_folder('edugraph-embeddings', local_filename, 'classification/zeroshot')

def write_dict_to_ldjson(data_dict, filename):
    try:
        with open(filename, 'w') as f:
            for key, value in data_dict.items():
                line_data = {"name": key, "embedding": value}
                f.write(json.dumps(line_data) + '\n')
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")

def upload_file_to_gcs_folder(bucket_name, source_file_name, destination_folder_name):
    """Uploads a file to a specific 'folder' in the GCS bucket.

    Args:
        bucket_name (str): The name of your GCS bucket.
        source_file_name (str): The path to your local file to upload.
        destination_folder_name (str): The 'folder' name within the bucket (e.g., 'my_data_folder').
                                       This should NOT end with a '/'.
    Returns:
        str: The public URL of the uploaded object, or None if upload fails.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Construct the full destination blob name including the folder prefix
    # If destination_folder_name is empty or None, it will upload to the root.
    if destination_folder_name:
        destination_blob_name = f"{destination_folder_name}/{os.path.basename(source_file_name)}"
    else:
        destination_blob_name = os.path.basename(source_file_name)

    blob = bucket.blob(destination_blob_name)

    try:
        blob.upload_from_filename(source_file_name)
        print(
            f"File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}."
        )
        # You can get the public URL if the object is publicly accessible
        # (Requires appropriate ACLs/permissions)
        # public_url = blob.public_url
        # print(f"Public URL: {public_url}")
        return blob.name  # Return the full object name in the bucket
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None


load_dotenv()

onto_path = "https://github.com/christian-bick/edugraph-ontology/releases/download/0.1.0/core-ontology.rdf"
ontology = load_from_path(onto_path)
generate_taxonomy_embeddings('Area', ontology)
generate_taxonomy_embeddings('Scope', ontology)
generate_taxonomy_embeddings('Ability', ontology)
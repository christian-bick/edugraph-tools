from typing import List, Optional

from dotenv import load_dotenv
from google.cloud import aiplatform
import os

from semantic.embeddings.embedder_google import GoogleMultiModalEmbedder
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import MatchNeighbor, Namespace


def read_file_as_blob(relative_file_path: str) -> Optional[bytes]:
    absolute_file_path = ""
    try:
        # Construct the absolute path
        # os.getcwd() gets the current working directory
        absolute_file_path = os.path.join(os.getcwd(), relative_file_path)

        with open(absolute_file_path, "rb") as f: # "rb" for reading in binary mode
            blob_content = f.read()
        return blob_content
    except FileNotFoundError:
        print(f"Error: File not found at '{absolute_file_path}'")
        return None
    except IOError as e:
        print(f"Error reading file '{absolute_file_path}': {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading '{absolute_file_path}': {e}")
        return None

def query_vector_search_index(
    project: str,
    location: str,
    index_endpoint: str, # The ID of your Index Endpoint, not the Index itself
    deployed_index: str, # The ID of the deployed index on the endpoint
    query_embedding: List[float],
    num_neighbors: int = 5,
    filter: Optional[List[Namespace]] = None,
) -> Optional[List[MatchNeighbor]]:
    try:
        # Initialize the AI Platform client
        aiplatform.init(project=project, location=location)

        # Get the Index Endpoint
        endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=index_endpoint
        )

        print(f"Initialized Index Endpoint: {index_endpoint}")

    except Exception as e:
        print(f"An error occurred endpoint initialization: {e}")
        return None

    try:
        print(f"Querying neighbors for an embedding with {len(query_embedding)} dimensions")

        # Perform the query
        response = endpoint.find_neighbors(
            deployed_index_id=deployed_index,
            queries=[query_embedding], # Expects a list of queries
            filter=filter,
            num_neighbors=num_neighbors
        )

        print(f"Successfully queried index. Found {len(response[0]) if response else 0} neighbors.")
        return response[0]

    except Exception as e:
        print(f"An error occurred during vector search query: {e}")
        return None



if __name__ == "__main__":
    load_dotenv()

    project = "edugraph-438718"
    location = "europe-west3"

    query_file = "./temp/query-example-1.png"
    query_blob = read_file_as_blob(query_file)

    if query_blob is None:
        exit(1)

    embedder = GoogleMultiModalEmbedder(
        model_name="multimodalembedding@001"
    )

    query_embeddings = embedder.embed_document("query_file", query_blob)

    neighbors = query_vector_search_index(
        project=project,
        location=location,
        index_endpoint="projects/575953891979/locations/europe-west3/indexEndpoints/6601907617818214400",
        deployed_index="example_deploy_1749682778003",
        query_embedding=query_embeddings[0]["embedding"],
        filter=[Namespace(
            name="type",
            allow_tokens=["taxonomy"]
        )]
    )

    neighbor_ids = [(neighbor.id, neighbor.distance) for neighbor in neighbors]

    print(neighbor_ids)



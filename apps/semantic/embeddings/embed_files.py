import os

import vertexai  # Only for type hinting if GenerativeModel is not directly imported
from dotenv import load_dotenv
from google.cloud import storage

from semantic.embeddings.embedder_google import GoogleMultiModalEmbedder, generate_jsonl_from_embeddings, \
    upload_blobs_as_new_files


class GoogleMultiModalBatchEmbedder:
    def __init__(self, project, location, bucket_name, embedder):
        self.project = project
        self.location = location
        self.bucket_name = bucket_name
        self.embedder = embedder

        vertexai.init(project=self.project, location=self.location)

    def embed_files(self, bucket_path, content_type, content_locale):
        bucket_path_raw = bucket_path + "/raw"
        bucket_path_normalized = bucket_path + "/normalized"
        bucket_path_embedded = bucket_path + "/embedded"

        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)

            prefix = bucket_path_raw
            if prefix and not prefix.endswith('/'):
                prefix += '/'

            blobs = bucket.list_blobs(prefix=prefix)

            print(
                f"Scanning folder '{bucket_path_raw if bucket_path_raw else 'root'}' in bucket '{self.bucket_name}'...")
            file_count = 0
            for blob in blobs:
                # Skip objects that represent folders (common convention is ending with '/')
                filename = os.path.basename(blob.name)
                if blob.name.endswith('/'):
                    continue

                file_count += 1
                print(f"Downloading and processing: {filename}")
                try:
                    file_content_bytes = blob.download_as_bytes()
                    embedding_results = self.embedder.embed_document(filename, file_content_bytes)
                    normalized_images = list(map(lambda x: (x["name"], x["image_data"]), embedding_results))
                    embeddings_data = list(map(lambda x: (x["name"], x["embedding"]), embedding_results))
                    embeddings_json = generate_jsonl_from_embeddings(embeddings_data, content_type=content_type,
                                                                     content_locale=content_locale)
                    upload_blobs_as_new_files(bucket_name=self.bucket_name,
                                              bucket_path=bucket_path_normalized,
                                              files_data=normalized_images)

                    json_filename = f"{filename.replace(".", "-")}.json"
                    upload_blobs_as_new_files(bucket_name=self.bucket_name,
                                              bucket_path=bucket_path_embedded,
                                              files_data=[(json_filename, embeddings_json.encode('utf-8'))])

                except Exception as e:
                    print(f"Error processing file {filename}: {e}")

            if file_count == 0:
                print(
                    f"No files found in '{bucket_path_raw if bucket_path_raw else 'root'}' of bucket '{self.bucket_name}'.")
            else:
                print(f"Finished processing {file_count} file(s).")

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    load_dotenv()
    embedder = GoogleMultiModalBatchEmbedder(
        project="edugraph-438718",
        location="europe-west3",
        bucket_name="edugraph-embed",
        embedder=GoogleMultiModalEmbedder(model_name="multimodalembedding@001"),
    )
    embedder.embed_files(bucket_path="examples", content_type=["material"], content_locale=["de", "de-DE"])

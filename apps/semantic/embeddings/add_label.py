import json
from google.cloud import storage
from typing import List, Dict, Any

from dotenv import load_dotenv

def process_jsonl_files_in_gcs(
    bucket_name: str,
    source_folder: str,
    target_folder: str,
    output_filename: str
) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    restricts_data: List[Dict[str, Any]] = [
        {
            "namespace": "type",
            "allow": ["material"]
        },
        {
            "namespace": "locale",
            "allow": ["de", "de-DE"]
        }
    ]

    all_modified_objects: List[Dict[str, Any]] = []
    processed_files_count = 0

    # Ensure source_folder has a trailing slash for prefix matching if not empty
    source_prefix = f"{source_folder.strip('/')}/" if source_folder.strip('/') else ""

    print(f"Scanning gs://{bucket_name}/{source_prefix} for JSONL files...")

    for blob in bucket.list_blobs(prefix=source_prefix):
        # Skip folder pseudo-objects and non-JSONL files (basic check)
        if blob.name.endswith('/') or not blob.name.lower().endswith((".jsonl", ".json")):
            if not blob.name.endswith('/'):  # Avoid logging for folders
                print(f"Skipping non-JSONL or folder object: {blob.name}")
            continue

        print(f"Processing file: gs://{bucket_name}/{blob.name}")
        try:
            file_content_bytes = blob.download_as_bytes()
            file_content_str = file_content_bytes.decode('utf-8')
            lines = file_content_str.strip().split('\n')
            file_objects_count = 0

            for line in lines:
                if not line.strip():  # Skip empty lines
                    continue
                try:
                    json_object = json.loads(line)
                    json_object["restricts"] = restricts_data
                    all_modified_objects.append(json_object)
                    file_objects_count += 1
                except json.JSONDecodeError as e:
                    print(f"  Warning: Could not decode JSON line in {blob.name}: '{line[:50]}...'. Error: {e}")
            if file_objects_count > 0:
                processed_files_count += 1
            print(f"  Processed {file_objects_count} JSON objects from {blob.name}")

        except Exception as e:
            print(f"  Error processing file {blob.name}: {e}")

    if not all_modified_objects:
        print("No JSON objects were processed or found. Output file will not be created.")
        return

    print(f"\nProcessed a total of {len(all_modified_objects)} JSON objects from {processed_files_count} files.")

    # Prepare the output content (JSONL)
    output_jsonl_content = "\n".join(json.dumps(obj) for obj in all_modified_objects)

    # Construct the full path for the output blob
    target_blob_name = f"{target_folder.strip('/')}/{output_filename.lstrip('/')}"
    if not target_folder.strip('/'):  # Handle case where target_folder is root
        target_blob_name = output_filename.lstrip('/')

    output_blob = bucket.blob(target_blob_name)

    try:
        output_blob.upload_from_string(output_jsonl_content.encode('utf-8'), content_type='application/jsonl')
        print(f"Successfully uploaded aggregated data to: gs://{bucket_name}/{target_blob_name}")
    except Exception as e:
        print(f"Error uploading aggregated data to gs://{bucket_name}/{target_blob_name}: {e}")


# Example Usage (replace with your actual values):
if __name__ == '__main__':
    load_dotenv()

    process_jsonl_files_in_gcs(
        bucket_name="edugraph-embed",
        source_folder="examples/embedded",
        target_folder="examples/embedded-with-labels",
        output_filename="all_items_with_labels.json"
    )

import json
import os
from typing import Optional, List, Dict, Tuple

import fitz
from google.cloud import storage
from vertexai.vision_models import MultiModalEmbeddingModel, Image


class GoogleMultiModalEmbedder:

    def __init__(self, model_name):
        self.model = MultiModalEmbeddingModel.from_pretrained(model_name)

    def embed_image(self,
                    image_blob: bytes,
                    ) -> Optional[List[float]]:
        try:
            # Load the multimodal embedding model
            # vertexai.init() is assumed to have been called externally

            # Create a Part object from the image bytes
            image = Image(image_blob)

            # Generate the embedding
            # For "multimodalembedding@001", the API expects a list of parts.
            embeddings = self.model.get_embeddings(image=image)

            # Extract the embedding vector
            if embeddings and embeddings.image_embedding:
                return embeddings.image_embedding  # Ensure it's a Python list
            else:
                print(
                    "Error: Could not extract embedding from Vertex AI response. Response structure might be unexpected.")
                return None

        except Exception as e:
            print(f"An error occurred during Vertex AI embedding generation: {e}")
            return None

    def embed_text(self,
                   text_content: str,
                   ) -> Optional[List[float]]:
        try:
            # Generate the embedding using the text input
            # The model can handle either text or image, or both for some tasks.
            # For a simple text embedding, we pass the text to the 'contextual_text' parameter.
            embeddings = self.model.get_embeddings(contextual_text=text_content)

            # Extract the text embedding vector
            if embeddings and embeddings.text_embedding:
                return embeddings.text_embedding
            else:
                print(
                    "Error: Could not extract text embedding from Vertex AI response.")
                return None
        except Exception as e:
            print(f"An error occurred during Vertex AI text embedding generation: {e}")
            return None

    def embed_document(self, filename, blob) -> List[Dict]:
        # Initialize image_blobs as a list to handle single non-PDFs and multiple PDF pages
        processed_image_blobs_with_names = []

        if filename.lower().endswith(".pdf"):
            pdf_pages_as_images = convert_pdf_blob_to_image_blobs(filename, blob)
            if pdf_pages_as_images:
                processed_image_blobs_with_names.extend(pdf_pages_as_images)
        else:
            # For non-PDFs, treat the blob as a single image
            # Ensure the filename for non-PDFs is correctly passed if needed for naming
            processed_image_blobs_with_names.append((filename, blob))

        embedding_results: List[Dict] = []

        for name, image_data in processed_image_blobs_with_names:
            # Determine mime_type based on filename extension if possible, or assume default
            mime_type = "image/png"  # Default, adjust if you handle other types like jpeg
            if name.lower().endswith(".jpg") or name.lower().endswith(".jpeg"):
                mime_type = "image/jpeg"

            embedding = self.embed_image(image_data)
            if embedding:
                embedding_results.append({
                    "name": name,
                    "mime_type": mime_type,
                    "embedding": embedding,
                    "image_data": image_data
                })
                print(f"Embedding for {name} (MIME: {mime_type}): {len(embedding)} dimensions")
            else:
                print(f"Failed to generate embedding for {name}")

        return embedding_results


def convert_pdf_blob_to_image_blobs(filename: str, pdf_blob: bytes, dpi: int = 300) -> Optional[
    List[Tuple[str, bytes]]]:
    image_blobs: List[(str, bytes)] = []
    try:
        # Open the PDF from the byte stream
        doc = fitz.open(stream=pdf_blob, filetype="pdf")

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Render page to an image (pixmap)
            # The matrix can be used for scaling. Default is identity matrix (no scaling).
            # Higher DPI increases resolution.
            pix = page.get_pixmap(dpi=dpi)

            # Get image bytes (default is PNG)
            img_bytes = pix.tobytes("png")
            if img_bytes:
                name_without_extension, _ = os.path.splitext(filename)
                name = "{}_{}.png".format(name_without_extension, page_num + 1)
                image_blobs.append((name, img_bytes))
            else:
                print(f"Warning: Could not get image bytes for page {page_num + 1}.")

        doc.close()
        return image_blobs
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return None


def generate_jsonl_from_embeddings(embeddings_data: List[Tuple[str, List[float]]],
                                   content_type: List[str], content_locale: List[str], restricts=None) -> str:


    if restricts is None:
        restricts = []

    restricts.extend([
        {
            "namespace": "type",
            "allow": content_type
        },
        {
            "namespace": "locale",
            "allow": content_locale
        }
    ])

    json_lines = []
    for name, embedding in embeddings_data:

        json_record = {
            "id": name,
            "embedding": embedding,
            "restricts": restricts
        }
        json_lines.append(json.dumps(json_record))
    return "\n".join(json_lines)


def upload_blobs_as_new_files(bucket_name: str,
                              bucket_path: str,
                              files_data: List[Tuple[str, bytes]]
                              ) -> None:
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        if not files_data:
            print(f"No files data provided to upload to gs://{bucket_name}/{bucket_path}.")
            return

        # Normalize the target folder path:
        # Remove leading/trailing slashes, then add a trailing slash if it's not the root.
        normalized_folder_path = bucket_path.strip('/')
        if normalized_folder_path:  # If path is not empty (i.e., not root)
            full_prefix = normalized_folder_path + '/'
        else:  # Path is empty, targeting bucket root
            full_prefix = ""

        for filename, content_blob in files_data:
            # Ensure filename itself doesn't have leading slashes if it's meant to be relative
            clean_filename = filename.lstrip('/')
            if not clean_filename:
                print(f"Skipping upload for an empty filename with blob of size {len(content_blob)} bytes.")
                continue

            full_gcs_file_path = f"{full_prefix}{clean_filename}"
            blob_object = bucket.blob(full_gcs_file_path)

            try:
                blob_object.upload_from_string(content_blob)
                print(f"Successfully uploaded '{clean_filename}' to gs://{bucket_name}/{full_gcs_file_path}")
            except Exception as e_upload:
                print(
                    f"Error uploading file '{clean_filename}' to gs://{bucket_name}/{full_gcs_file_path}: {e_upload}")

    except Exception as e_client:
        print(f"An error occurred during GCS operation for bucket '{bucket_name}': {e_client}")

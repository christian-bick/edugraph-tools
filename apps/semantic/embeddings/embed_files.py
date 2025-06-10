import os
from typing import Callable, Tuple, Dict
from typing import List, Optional

import fitz
import vertexai  # Only for type hinting if GenerativeModel is not directly imported
from dotenv import load_dotenv
from google.cloud import storage
from vertexai.vision_models import MultiModalEmbeddingModel, Image


def convert_pdf_blob_to_image_blobs(filename: str, pdf_blob: bytes, dpi: int = 300) -> Optional[
    List[Tuple[str, bytes]]]:
    """
    Converts each page of a PDF (provided as a byte blob) into an image (PNG format)
    and returns a list of image byte blobs.

    Args:
        filename (str): The corresponding filename
        pdf_blob (bytes): The content of the PDF file as bytes.
        dpi (int): Dots per inch for rendering the PDF pages to images.
                     Higher DPI results in larger and higher-quality images.

    Returns:
        Optional[List[bytes]]: A list of byte blobs, where each blob is the
                               content of a generated PNG image for a page.
                               Returns None if an error occurs during PDF processing.
    """
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

def save_images_to_temp_directory(self, image_data_list: List[Tuple[str, bytes]]) -> None:
    """
    Saves a list of images to a 'temp' directory relative to the current working directory.

    Each item in the list should be a tuple containing the desired filename (str)
    and the image data (bytes).

    Args:
        image_data_list (List[Tuple[str, bytes]]): A list of (filename, image_bytes) tuples.
    """
    temp_dir = "temp"
    try:
        # Create the 'temp' directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Ensured directory '{temp_dir}' exists or was created.")

        for filename, image_blob in image_data_list:
            file_path = os.path.join(temp_dir, filename)
            try:
                with open(file_path, "wb") as f:
                    f.write(image_blob)
                print(f"Successfully saved: {file_path}")
            except IOError as e:
                print(f"Error saving file {filename} to {file_path}: {e}")
    except OSError as e:
        print(f"Error creating directory {temp_dir}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def generate_jsonl_from_embeddings(embeddings_data: List[Tuple[str, List[float]]]
                                   ) -> str:
    """
    Generates a JSON Lines (JSONL) formatted string from a list of (name, embedding) tuples.

    Each line in the output string will be a JSON object of the form:
    {"name": "some_name", "embedding": [0.1, 0.2, ...]}

    Args:
        embeddings_data (List[Tuple[str, List[float]]]): A list of tuples,
            where each tuple contains:
            - A name (str) for the item.
            - An embedding vector (List[float]).

    Returns:
        str: A string where each line is a JSON object representing an embedding.
    """
    json_lines = []
    for name, embedding in embeddings_data:
        json_record = {"name": name, "embedding": embedding}
        json_lines.append(json.dumps(json_record))
    return "\n".join(json_lines)


class GoogleFileEmbedder:

    def __init__(self, project, location, bucket_name, bucket_path, model_name):
        self.project = project
        self.location = location
        self.bucket_name = bucket_name
        self.bucket_path = bucket_path
        self.model = MultiModalEmbeddingModel.from_pretrained(model_name)

    def generate_multimodal_embedding_from_image_blob(self,
                                                      image_blob: bytes,
                                                      ) -> Optional[List[float]]:
        """
        Generates a multimodal embedding for an image provided as a byte blob
        using an already initialized Vertex AI client.
    
        Args:
            image_blob (bytes): The content of the image file as bytes.
    
        Returns:
            Optional[List[float]]: A list of floats representing the embedding vector,
                                   or None if an error occurs.
        """
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

    def upload_blobs_as_new_files(self,
                                  bucket_path: str,
                                  files_data: List[Tuple[str, bytes]]
                                  ) -> None:
        """
        Uploads a list of (filename, blob_content) tuples as new, separate files
        to a specified folder path within the Google Cloud Storage bucket.
        If a file with the same name already exists at the target path, it will be overwritten.

        Args:
            bucket_path (str): The destination folder path within the bucket
                                          (e.g., "output/images" or "" for the root).
                                          This path is relative to the bucket root.
            files_data (List[Tuple[str, bytes]]): A list of tuples, where each
                tuple contains:
                - filename (str): The desired name for the file in GCS.
                - blob_content (bytes): The content of the file.
        """
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)

            if not files_data:
                print(f"No files data provided to upload to gs://{self.bucket_name}/{bucket_path}.")
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
                    print(f"Successfully uploaded '{clean_filename}' to gs://{self.bucket_name}/{full_gcs_file_path}")
                except Exception as e_upload:
                    print(
                        f"Error uploading file '{clean_filename}' to gs://{self.bucket_name}/{full_gcs_file_path}: {e_upload}")

        except Exception as e_client:
            print(f"An error occurred during GCS operation for bucket '{self.bucket_name}': {e_client}")

    def embed_blob(self, filename, blob) -> List[Dict]:
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

            # save_images_to_temp_directory(processed_image_blobs_with_names)

        embedding_results: List[Dict] = []

        for name, image_data in processed_image_blobs_with_names:
            # Determine mime_type based on filename extension if possible, or assume default
            mime_type = "image/png"  # Default, adjust if you handle other types like jpeg
            if name.lower().endswith(".jpg") or name.lower().endswith(".jpeg"):
                mime_type = "image/jpeg"

            embedding = self.generate_multimodal_embedding_from_image_blob(image_data)
            if embedding:
                embedding_results.append({
                    name: name,
                    mime_type: mime_type,
                    embedding: embedding,
                    image_data: image_data
                })
                print(f"Embedding for {name} (MIME: {mime_type}): {len(embedding)} dimensions")
            else:
                print(f"Failed to generate embedding for {name}")

        return embedding_results

    def embed_files(self):
        # Initialize Vertex AI *before* it's needed by the callback
        print(f"Initializing Vertex AI for project: {self.project}, location: {self.location}")
        try:
            vertexai.init(project=self.project, location=self.location)
            print("Vertex AI initialized successfully.")
        except Exception as e:
            print(f"Error initializing Vertex AI: {e}")
            return  # Stop execution if Vertex AI can't be initialized

        bucket_path = self.bucket_path + "/raw"

        """
        Downloads all files within a specified folder of a Google Cloud Storage bucket
        and calls a provided function with each file's name and content.

        Args:
            bucket_path (str): The path to the folder within the bucket (e.g., "path/to/your/folder").
                               Use an empty string "" for the root of the bucket.
                               The path should not start with a '/'.
            callback (Callable[[str, bytes], None]): A function to be called
                               for each downloaded file. It will receive two arguments:
                               - blob_name (str): The full GCS path of the file (e.g., "path/to/your/folder/file.txt").
                               - file_content (bytes): The content of the file as bytes.
        """
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)

            prefix = bucket_path
            if prefix and not prefix.endswith('/'):
                prefix += '/'

            blobs = bucket.list_blobs(prefix=prefix)

            print(f"Scanning folder '{bucket_path if bucket_path else 'root'}' in bucket '{self.bucket_name}'...")
            file_count = 0
            for blob in blobs:
                # Skip objects that represent folders (common convention is ending with '/')
                filename = blob.name
                if filename.endswith('/'):
                    continue

                file_count += 1
                print(f"Downloading and processing: {filename}")
                try:
                    file_content_bytes = blob.download_as_bytes()
                    embedding_results = self.embed_blob(filename, file_content_bytes)
                    print(embedding_results)

                    normalized_images = list(map(lambda x: (x.name, x.image_data), embedding_results))
                    embeddings_data = list(map(lambda x: (x.name, x.embedding), embedding_results))
                    embeddings_json = generate_jsonl_from_embeddings(embeddings_data)
                    self.upload_blobs_as_new_files(self.bucket_path + "/normalized", normalized_images)
                    self.upload_blobs_as_new_files(self.bucket_path + "/embedded", [filename, embeddings_json])

                except Exception as e:
                    print(f"Error processing file {filename}: {e}")

            if file_count == 0:
                print(f"No files found in '{bucket_path if bucket_path else 'root'}' of bucket '{self.bucket_name}'.")
            else:
                print(f"Finished processing {file_count} file(s).")

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    load_dotenv()
    embedder = GoogleFileEmbedder(
        project="edugraph-438718",
        location="europe-west3",
        bucket_name="edugraph-material",
        bucket_path="examples",
        model_name="multimodalembedding@001",
    )
    embedder.embed_files()

import os
import uuid
from typing import Callable, Tuple
from typing import List, Optional

import fitz
import vertexai  # Only for type hinting if GenerativeModel is not directly imported
from dotenv import load_dotenv
from google.cloud import storage
from vertexai.vision_models  import MultiModalEmbeddingModel, Image


def download_gcs_folder_files_and_process(
    bucket_name: str,
    bucket_path: str,
    callback: Callable[[str, bytes], None]
) -> None:
    """
    Downloads all files within a specified folder of a Google Cloud Storage bucket
    and calls a provided function with each file's name and content.

    Args:
        bucket_name (str): The name of the GCS bucket.
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
        bucket = storage_client.bucket(bucket_name)

        # Ensure the prefix correctly targets files within the folder.
        # If folder_path is "foo/bar", prefix becomes "foo/bar/".
        # If folder_path is "" (root), prefix remains "".
        prefix = bucket_path
        if prefix and not prefix.endswith('/'):
            prefix += '/'

        blobs = bucket.list_blobs(prefix=prefix)

        print(f"Scanning folder '{bucket_path if bucket_path else 'root'}' in bucket '{bucket_name}'...")
        file_count = 0
        for blob in blobs:
            # Skip objects that represent folders (common convention is ending with '/')
            if blob.name.endswith('/'):
                continue

            file_count += 1
            print(f"Downloading and processing: {blob.name}")
            try:
                file_content_bytes = blob.download_as_bytes()
                callback(blob.name, file_content_bytes)
            except Exception as e:
                print(f"Error processing file {blob.name}: {e}")

        if file_count == 0:
            print(f"No files found in '{bucket_path if bucket_path else 'root'}' of bucket '{bucket_name}'.")
        else:
            print(f"Finished processing {file_count} file(s).")

    except Exception as e:
        print(f"An error occurred: {e}")


def convert_pdf_blob_to_image_blobs(pdf_blob: bytes, dpi: int = 300) -> Optional[List[Tuple[str, bytes]]]:
    """
    Converts each page of a PDF (provided as a byte blob) into an image (PNG format)
    and returns a list of image byte blobs.

    Args:
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
                name = "{}_{}.png".format(str(uuid.uuid4()), page_num + 1)
                image_blobs.append((name, img_bytes))
            else:
                print(f"Warning: Could not get image bytes for page {page_num + 1}.")

        doc.close()
        return image_blobs
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return None


def generate_multimodal_embedding_from_image_blob(
    image_blob: bytes,
    model_name: str = "multimodalembedding@001",
    mime_type: str = "image/png"  # Common default, adjust if your images are usually JPEG, etc.
) -> Optional[List[float]]:
    """
    Generates a multimodal embedding for an image provided as a byte blob
    using an already initialized Vertex AI client.

    Args:
        image_blob (bytes): The content of the image file as bytes.
        model_name (str): The name of the multimodal embedding model to use.
                          Defaults to "multimodalembedding@001".
        mime_type (str): The MIME type of the image (e.g., "image/png", "image/jpeg").

    Returns:
        Optional[List[float]]: A list of floats representing the embedding vector,
                               or None if an error occurs.
    """
    try:
        # Load the multimodal embedding model
        # vertexai.init() is assumed to have been called externally
        model = MultiModalEmbeddingModel.from_pretrained(model_name)

        # Create a Part object from the image bytes
        image = Image(image_blob)

        # Generate the embedding
        # For "multimodalembedding@001", the API expects a list of parts.
        embeddings = model.get_embeddings(image=image)

        # Extract the embedding vector
        if embeddings and embeddings.image_embedding:
            return embeddings.image_embedding  # Ensure it's a Python list
        else:
            print("Error: Could not extract embedding from Vertex AI response. Response structure might be unexpected.")
            return None

    except Exception as e:
        print(f"An error occurred during Vertex AI embedding generation: {e}")
        return None


def save_images_to_temp_directory(image_data_list: List[Tuple[str, bytes]]) -> None:
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


# Example Usage (assuming you have image_data_list populated):
#
# example_images = [
#     ("image1.png", b"some_png_bytes_here"),
#     ("photo_A.jpg", b"some_jpeg_bytes_here")
# ]
# save_images_to_temp_directory(example_images)

def embed_blob(filename, blob):
    # Initialize image_blobs as a list to handle single non-PDFs and multiple PDF pages
    processed_image_blobs_with_names = []

    if filename.lower().endswith(".pdf"):
        pdf_pages_as_images = convert_pdf_blob_to_image_blobs(blob)
        if pdf_pages_as_images:
            processed_image_blobs_with_names.extend(pdf_pages_as_images)
    else:
        # For non-PDFs, treat the blob as a single image
        # Ensure the filename for non-PDFs is correctly passed if needed for naming
        processed_image_blobs_with_names.append((filename, blob))

    # save_images_to_temp_directory(processed_image_blobs_with_names)

    for name, image_data in processed_image_blobs_with_names:
        # Determine mime_type based on filename extension if possible, or assume default
        mime_type = "image/png"  # Default, adjust if you handle other types like jpeg
        if name.lower().endswith(".jpg") or name.lower().endswith(".jpeg"):
            mime_type = "image/jpeg"

        embedding = generate_multimodal_embedding_from_image_blob(image_data, mime_type=mime_type)
        if embedding:
            print(f"Embedding for {name} (MIME: {mime_type}): {len(embedding)} dimensions")
        else:
            print(f"Failed to generate embedding for {name}")


project = "edugraph-438718"
location = "europe-west3"
bucket_name = "edugraph-material"
bucket_path = "examples/lernwolf-math-primary"


def embed_files():
    load_dotenv()
    # Initialize Vertex AI *before* it's needed by the callback
    print(f"Initializing Vertex AI for project: {project}, location: {location}")
    try:
        vertexai.init(project=project, location=location)
        print("Vertex AI initialized successfully.")
    except Exception as e:
        print(f"Error initializing Vertex AI: {e}")
        return  # Stop execution if Vertex AI can't be initialized

    download_gcs_folder_files_and_process(
        bucket_name=bucket_name,
        bucket_path=bucket_path,
        callback=embed_blob
    )


embed_files()

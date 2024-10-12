from io import BytesIO
from uuid import uuid4

from flask import Flask, request

from semantic.gemini_classifier import GeminiClassifier
from semantic.gemini_file_storage import GeminiFileStorage
from semantic.gemini_prompt_strategy import GeminiPromptStrategy
from semantic.ontology_loader import OntologyLoader

app = Flask(__name__, static_folder=None)

onto = OntologyLoader.load_from_path("./../core-ontology.rdf")

@app.route("/")
def root():
    return "Hello, World!"

@app.route("/classify", methods=["POST"])
def classify():
    file_upload = request.files['file']
    mime_type = file_upload.mimetype
    name = str(uuid4())
    file = GeminiFileStorage.upload(name, mime_type, BytesIO(file_upload.stream.read()))
    classifier = GeminiClassifier(onto, GeminiPromptStrategy)
    classification = classifier.classify_content(file)
    return classification

def create_app():
    return app
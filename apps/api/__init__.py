from io import BytesIO
from uuid import uuid4

from flask import Flask, request
from google import generativeai as gemini

from semantic import GeminiClassifier
from semantic import GeminiFileStorage
from semantic import GeminiPromptStrategy
from semantic import OntologyLoader
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder=None)

onto = OntologyLoader.load_from_path("./../core-ontology.rdf")

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

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
from io import BytesIO
from uuid import uuid4

from flask import Flask, request, jsonify

from semantic import GeminiFileStorage
from semantic import OntologyLoader
from semantic import OntologyUtil
from semantic.classifiers import SplitPromptClassifier
from semantic.classifiers import SplitPromptStrategyGemini
from .ontology_serializer import serialize_entity_tree

app = Flask(__name__, static_folder=None)

onto = OntologyLoader.load_from_path("./../core-ontology.rdf")
onto_util = OntologyUtil(onto)

root_areas = onto_util.list_root_entities(onto.Area)
root_abilities = onto_util.list_root_entities(onto.Ability)
root_scopes = onto_util.list_root_entities(onto.Scope)

@app.route("/")
def root():
    return "Hello, World!"

@app.route("/classify", methods=["POST"])
def classify():
    file_upload = request.files['file']
    mime_type = file_upload.mimetype
    name = str(uuid4())
    file = GeminiFileStorage.upload(name, mime_type, BytesIO(file_upload.stream.read()))
    classifier = SplitPromptClassifier(onto, SplitPromptStrategyGemini)
    classification = classifier.classify_content(file)
    return classification

@app.route("/ontology", methods=["GET"])
def ontology():
    return jsonify({
        "areas": serialize_entity_tree(root_areas),
        "abilities": serialize_entity_tree(root_abilities),
        "scopes": serialize_entity_tree(root_scopes)
    })

def create_app():
    return app
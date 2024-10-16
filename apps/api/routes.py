from io import BytesIO
from uuid import uuid4

from flask import Flask, request, jsonify
from flask_cors import CORS

from semantic.ontology_util import OntologyUtil
from semantic.classifiers import SplitPromptClassifier
from semantic.classifiers import SplitPromptStrategyGemini
from semantic.gemini_file_storage import upload_file
from semantic.ontology_loader import load_from_path
from .ontology_serializer import serialize_entity_tree, serialize_entities_with_names

app = Flask(__name__, static_folder=None)

onto = load_from_path("./core-ontology.rdf")
onto_util = OntologyUtil(onto)

root_areas = onto_util.list_root_entities(onto.Area)
root_abilities = onto_util.list_root_entities(onto.Ability)
root_scopes = onto_util.list_root_entities(onto.Scope)

@app.route("/")
def root():
    return "OK"

@app.route("/classify", methods=["POST"])
def classify():
    file_upload = request.files['file']
    mime_type = file_upload.mimetype
    name = str(uuid4())
    file = upload_file(name, mime_type, BytesIO(file_upload.stream.read()))
    classifier = SplitPromptClassifier(onto, SplitPromptStrategyGemini)
    classification = classifier.classify_content(file)
    return jsonify({
        "areas": serialize_entities_with_names(classification["areas"]),
        "abilities": serialize_entities_with_names(classification["abilities"]),
        "scopes": serialize_entities_with_names(classification["scopes"])
    })

@app.route("/ontology", methods=["GET"])
def ontology():
    return jsonify({
        "areas": serialize_entity_tree(root_areas),
        "abilities": serialize_entity_tree(root_abilities),
        "scopes": serialize_entity_tree(root_scopes)
    })

def create_app():
    CORS(app)
    return app
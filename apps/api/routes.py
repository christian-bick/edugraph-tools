import ctypes
from io import BytesIO
from uuid import uuid4

from flask import Flask, request, jsonify
from flask_cors import CORS
from google.generativeai import get_file

from semantic.ontology_util import OntologyUtil
from semantic.classifiers import SplitPromptClassifier
from semantic.classifiers import SplitPromptStrategyGemini
from semantic.gemini_file_storage import upload_file
from semantic.ontology_loader import load_from_path
from .classification_cache import ClassificationCache
from .ontology_serializer import serialize_entity_tree, serialize_entities_with_names

app = Flask(__name__, static_folder=None)

onto = load_from_path("./core-ontology.rdf")
onto_util = OntologyUtil(onto)

classification_cache = ClassificationCache()

root_areas = onto_util.list_root_entities(onto.Area)
root_abilities = onto_util.list_root_entities(onto.Ability)
root_scopes = onto_util.list_root_entities(onto.Scope)

@app.route("/")
def root():
    return "OK"

@app.route("/classify", methods=["POST"])
def classify():
    request_name = request.values['name']
    request_file = request.files['file']

    if request_name is None or request_name == '':
        name = str(uuid4())
    else:
        name = request_name

    name = str(ctypes.c_size_t(hash(name)).value)

    result = classification_cache.get(name)

    if result is not None:
        app.logger.info('classification used from cache')
    else:
        app.logger.info('classification starting')
        mime_type = request_file.mimetype

        file = None
        try:
            file = get_file(name)
            app.logger.info('file %s retrieved from gemini', name)
        except:
            app.logger.info('file %s not in gemini', name)

        if file is None:
            file = upload_file(name, mime_type, BytesIO(request_file.stream.read()))
            app.logger.info('file %s added to gemini', name)

        classifier = SplitPromptClassifier(onto, SplitPromptStrategyGemini)
        classification = classifier.classify_content(file)

        result= jsonify({
            "areas": serialize_entities_with_names(classification["areas"]),
            "abilities": serialize_entities_with_names(classification["abilities"]),
            "scopes": serialize_entities_with_names(classification["scopes"])
        })

        classification_cache.update(name, result)

    return result

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
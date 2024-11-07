import ctypes
from io import BytesIO
from uuid import uuid4

from flask import Flask, request, jsonify
from flask_cors import CORS
from google.generativeai import get_file

from semantic.classifiers.classifier_split import ClassifierSplit
from semantic.classifiers.strategies.classifier_split_gemini_with_serialized_taxonomies_v1 import \
    ClassifierSplitGeminiWithSerializedTaxonomiesV1
from semantic.gemini_file_storage import upload_file
from semantic.ontology_loader import load_from_path
from semantic.ontology_util import OntologyUtil
from .classification_cache import ClassificationCache
from .ontology_serializer import serialize_entity_tree, serialize_entities_with_names, \
    serialize_entity_tree_with_parent_relations

app = Flask(__name__, static_folder=None)


onto_ttl = "./core-ontology.ttl"
onto_path = "./core-ontology.rdf"
onto = load_from_path(onto_path)
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

        classifier = ClassifierSplit(ClassifierSplitGeminiWithSerializedTaxonomiesV1(onto))
        classification = classifier.classify_content(file)
        classified_area = getattr(onto, classification["Area"][0])

        result = jsonify({
            "classification": {
                "areas": serialize_entities_with_names(classification["Area"]),
                "abilities": serialize_entities_with_names(classification["Ability"]),
                "scopes": serialize_entities_with_names(classification["Scope"]),
            },
            "expansion": {
                "areas": serialize_entity_tree_with_parent_relations([ classified_area ], "expandsArea", "partOfArea"),
            }
        })

        classification_cache.update(name, result)

    return result


@app.route("/ontology", methods=["GET"])
def ontology():
    return jsonify({
        "taxonomy": {
            "areas": serialize_entity_tree(root_areas, "hasPartArea"),
            "abilities": serialize_entity_tree(root_abilities, "hasPartAbility"),
            "scopes": serialize_entity_tree(root_scopes, "hasPartScope")
        }})


def create_app():
    CORS(app)
    return app

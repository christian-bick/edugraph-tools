from io import BytesIO
from uuid import uuid4

from flask import Flask, request

from semantic.gemini_file_storage import GeminiFileStorage

app = Flask(__name__, static_folder=None)

@app.route("/")
def root():
    return "Hello, World!"

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    mime_type = request.mimetype
    name = str(uuid4())
    GeminiFileStorage.upload(name, mime_type, BytesIO(file.stream.read()))
    return {
        "file_id": uuid4()
    }

@app.route("/classify/<string:file_id>", methods=["GET"])
def classify():
    return "Classify"

def create_app():
    return app
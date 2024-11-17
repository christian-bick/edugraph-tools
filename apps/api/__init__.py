from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

app = Flask(__name__, static_folder=None)

from api import routes


def create_app():
    load_dotenv()
    CORS(app)
    return app

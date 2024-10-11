from flask import Flask
from semantic import *

app = Flask(__name__, static_folder=None)

@app.route("/")
def root():
    return "<p>Hello, World!</p>"

def create_app():
    return app
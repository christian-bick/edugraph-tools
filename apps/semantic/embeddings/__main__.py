import os

from dotenv import load_dotenv
from google import generativeai as gemini

from semantic.ontology_loader import load_from_path

load_dotenv()

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

example_file = "./../examples/LongMultiplication-01.png"

onto = load_from_path("./core-ontology.rdf")


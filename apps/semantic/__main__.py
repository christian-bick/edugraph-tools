import os

from semantic.gemini_classifier import GeminiClassifier
from google import generativeai as gemini
from semantic.gemini_prompt_strategy import GeminiPromptStrategy
from semantic.ontology_loader import OntologyLoader
from dotenv import load_dotenv

load_dotenv()

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

example_file = "./../examples/LongMultiplication-01.png"

onto = OntologyLoader.load_from_path("./../core-ontology.rdf")
classifier = GeminiClassifier(onto, GeminiPromptStrategy)
result = classifier.classify_content(example_file)

print(result)
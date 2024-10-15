import os

from dotenv import load_dotenv
from google import generativeai as gemini

from semantic.classifiers import SplitPromptClassifier
from semantic.classifiers import SplitPromptStrategyGemini
from semantic.gemini_file_storage import upload_file
from semantic.ontology_loader import load_from_path

load_dotenv()

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

example_file = "./../examples/LongMultiplication-01.png"

onto = load_from_path("./../core-ontology.rdf")
file = upload_file('example-file', 'image/png', example_file)

classifier = SplitPromptClassifier(onto, SplitPromptStrategyGemini)
result = classifier.classify_content(example_file)

print(result)
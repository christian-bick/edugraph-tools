
import google.generativeai as gemini
import os

from owlready2 import get_ontology

from semantic.gemini_classifier import GeminiClassifier

from semantic.gemini_prompt_strategy import GeminiPromptStrategy

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

onto = get_ontology("./../core-ontology.rdf").load()
onto.base_iri = "http://edugraph.io/edu#"

example_file = "./../examples/LongMultiplication-01.png"

classifier = GeminiClassifier(onto, GeminiPromptStrategy)
result = classifier.classify_content(example_file)

print(result)
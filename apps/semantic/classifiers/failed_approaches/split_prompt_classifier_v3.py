import typing
import google.generativeai as gemini
import json

from semantic.classifiers.failed_approaches.split_prompt_strategy_gemini_v2 import SplitPromptStrategyGeminiV2

class PromptResponse(typing.TypedDict):
    Area: list[str]
    Ability: list[str]
    Scope: list[str]


prompt = """
You are provided with two files. 

The first file contains an open web ontology provided to you in the "text/turtle" format. 

The ontology provides 3 types of descriptors for classification:

Area = edu:Area = http://edugraph.io/edu#Area 
Ability = edu:Ability = http://edugraph.io/edu#Ability
Scope = edu:Scope = http://edugraph.io/edu#Scope

A definition is provided for each term through the "rdfs:isDefinedBy" annotation. Use it during
classification to identify matching terms during classification.

The second file contains the learning material to classify in the terms of the ontology. 

Classify the second file as follows:

- Determine matching areas from the terms that have "rdf:type" "edu:Area"
- Determine matching abilities from the terms that have "rdf:type" "edu:Ability"
- Determine matching scopes from the terms that have "rdf:type" "edu:Scope"

- Skip the "edu:" prefix when returning the terms

- Return exactly one area
- Return no more than 5 abilities
- Return no more than 10 scopes
"""

class SplitPromptClassifierV3:

    def __init__(self, onto, model):
        self.onto = onto
        self.ClassifierStrategy = SplitPromptStrategyGeminiV2
        self.model = model

    def classify_content(self, file, ontology_file):
        result = self.model.generate_content(
            [prompt, ontology_file, file], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptResponse
            ))
        print(result.text)
        result_obj = json.loads(result.text)
        print(result_obj)
        return result_obj
